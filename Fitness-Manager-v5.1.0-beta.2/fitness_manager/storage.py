"""Backup, verification, and restore operations."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from . import crypto
from .db import APP_DIR, DB_PATH, connect, integrity_check, initialize


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_manifest(path: Path, *, encrypted: bool = False) -> Path:
    manifest = {
        "format": "fitness-manager-backup-v1",
        "file": path.name,
        "sha256": sha256_file(path),
        "encrypted": encrypted,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    manifest_path = path.with_suffix(path.suffix + ".json")
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    if os.name != "nt":
        manifest_path.chmod(0o600)
    return manifest_path


def verify_backup(path: Path, *, require_manifest: bool = True) -> None:
    if not path.is_file():
        raise FileNotFoundError(path)
    if path.suffix == ".enc":
        if not path.read_bytes().startswith(crypto.MAGIC):
            raise ValueError("Encrypted backup header is invalid")
    else:
        manifest_path = path.with_suffix(path.suffix + ".json")
        if not manifest_path.exists():
            if require_manifest:
                raise ValueError("Backup manifest missing; refusing unverified restore")
        else:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest.get("file") != path.name or manifest.get("sha256") != sha256_file(path):
                raise ValueError("Backup checksum mismatch")
        result = integrity_check(path)
        if result != "ok":
            raise ValueError(f"SQLite integrity check failed: {result}")


def create_backup(db_path: Path = DB_PATH, backup_dir: Path | None = None) -> Path:
    if not db_path.exists():
        initialize(db_path)
    destination_dir = Path(backup_dir or (APP_DIR / "backups"))
    destination_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    if os.name != "nt":
        destination_dir.chmod(0o700)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    target = destination_dir / f"fitness_manager_{stamp}.sqlite"
    source = sqlite3.connect(str(db_path))
    destination = sqlite3.connect(str(target))
    try:
        source.backup(destination)
    finally:
        destination.close()
        source.close()
    if integrity_check(target) != "ok":
        target.unlink(missing_ok=True)
        raise ValueError("New backup failed SQLite integrity check")
    if os.name != "nt":
        target.chmod(0o600)
    _write_manifest(target)
    # Keep the 30 most recent verified local snapshots.
    snapshots = sorted(destination_dir.glob("fitness_manager_*.sqlite"), key=lambda item: item.stat().st_mtime, reverse=True)
    for stale in snapshots[30:]:
        stale.unlink(missing_ok=True)
        stale.with_suffix(stale.suffix + ".json").unlink(missing_ok=True)
    return target


def maybe_encrypt_for_drive(backup: Path, drive_dir: Path, passphrase: str | None) -> Path:
    if not passphrase:
        raise ValueError("Drive backup blocked: FITNESS_MANAGER_BACKUP_PASSPHRASE is not configured")
    encrypted = Path(drive_dir).expanduser() / (backup.name + ".enc")
    crypto.encrypt_file(backup, encrypted, passphrase)
    _write_manifest(encrypted, encrypted=True)
    return encrypted


def restore_backup(source: Path, db_path: Path = DB_PATH, passphrase: str | None = None) -> Path:
    source = Path(source).expanduser()
    db_path = Path(db_path).expanduser()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        if source.suffix == ".enc":
            manifest_path = source.with_suffix(source.suffix + ".json")
            if not manifest_path.exists():
                raise ValueError("Encrypted backup manifest missing")
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest.get("file") != source.name or manifest.get("encrypted") is not True:
                raise ValueError("Encrypted backup manifest metadata is invalid")
            if manifest.get("sha256") != sha256_file(source):
                raise ValueError("Encrypted backup checksum mismatch")
            fd, name = tempfile.mkstemp(prefix="fm-restore-", suffix=".sqlite", dir=str(db_path.parent))
            os.close(fd)
            temporary = Path(name)
            crypto.decrypt_file(source, temporary, passphrase or "")
            if integrity_check(temporary) != "ok":
                raise ValueError("Decrypted SQLite database failed integrity check")
        else:
            verify_backup(source, require_manifest=True)
            temporary = source

        if db_path.exists():
            safety_dir = db_path.parent / "pre-restore"
            safety_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
            if os.name != "nt":
                safety_dir.chmod(0o700)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            safety_path = safety_dir / f"pre_restore_{stamp}.sqlite"
            src = sqlite3.connect(str(db_path))
            dst = sqlite3.connect(str(safety_path))
            try:
                src.backup(dst)
            finally:
                dst.close()
                src.close()
            if integrity_check(safety_path) != "ok":
                safety_path.unlink(missing_ok=True)
                raise ValueError("Pre-restore safety copy failed integrity check")
            _write_manifest(safety_path)

        staged = db_path.with_suffix(db_path.suffix + ".restore-staging")
        shutil.copy2(temporary, staged)
        if os.name != "nt":
            staged.chmod(0o600)
        if integrity_check(staged) != "ok":
            staged.unlink(missing_ok=True)
            raise ValueError("Staged restore failed integrity check")
        os.replace(staged, db_path)
        return db_path
    finally:
        if temporary is not None and temporary != source:
            temporary.unlink(missing_ok=True)
