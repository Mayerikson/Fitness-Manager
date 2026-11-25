"""Optional authenticated encryption for cloud-bound backup copies."""
from __future__ import annotations

import os
from pathlib import Path

MAGIC = b"FMENC1"
SALT_BYTES = 16
NONCE_BYTES = 12


class EncryptionUnavailable(RuntimeError):
    pass


def _crypto():
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
    except ImportError as exc:
        raise EncryptionUnavailable(
            "Optional dependency missing. Install with: pip install -r requirements-backup-encryption.txt"
        ) from exc
    return AESGCM, Scrypt


def encrypt_file(source: Path, destination: Path, passphrase: str) -> None:
    if len(passphrase or "") < 12:
        raise ValueError("Backup passphrase must contain at least 12 characters")
    AESGCM, Scrypt = _crypto()
    salt, nonce = os.urandom(SALT_BYTES), os.urandom(NONCE_BYTES)
    key = Scrypt(salt=salt, length=32, n=2**15, r=8, p=1).derive(passphrase.encode("utf-8"))
    header = MAGIC + salt + nonce
    ciphertext = AESGCM(key).encrypt(nonce, source.read_bytes(), header)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(header + ciphertext)
    if os.name != "nt":
        destination.chmod(0o600)


def decrypt_file(source: Path, destination: Path, passphrase: str) -> None:
    if len(passphrase or "") < 12:
        raise ValueError("Backup passphrase must contain at least 12 characters")
    AESGCM, Scrypt = _crypto()
    payload = source.read_bytes()
    minimum = len(MAGIC) + SALT_BYTES + NONCE_BYTES + 16
    if len(payload) < minimum or not payload.startswith(MAGIC):
        raise ValueError("Unrecognized or truncated encrypted backup")
    offset = len(MAGIC)
    salt = payload[offset:offset + SALT_BYTES]
    nonce = payload[offset + SALT_BYTES:offset + SALT_BYTES + NONCE_BYTES]
    header = payload[:offset + SALT_BYTES + NONCE_BYTES]
    ciphertext = payload[len(header):]
    key = Scrypt(salt=salt, length=32, n=2**15, r=8, p=1).derive(passphrase.encode("utf-8"))
    plaintext = AESGCM(key).decrypt(nonce, ciphertext, header)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(plaintext)
    if os.name != "nt":
        destination.chmod(0o600)
