#!/usr/bin/env python3
"""Small release-hygiene audit; not a SAST or malware scanner."""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

FORBIDDEN_PARTS = {".git", ".venv", "venv", "node_modules", "backups", "pre-restore"}
FORBIDDEN_SUFFIXES = {".sqlite", ".sqlite3", ".sqlite.enc", ".sqlite.json", ".pyc"}
SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]{12,}['\"]"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]


def audit(root: Path) -> list[str]:
    issues = []
    root = root.resolve()
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in FORBIDDEN_PARTS for part in rel.parts):
            continue
        if "__pycache__" in rel.parts:
            issues.append(f"Python cache directory must not be distributed: {rel}")
            continue
        if path.name.lower().endswith(tuple(FORBIDDEN_SUFFIXES)):
            issues.append(f"Private database/backup artifact: {rel}")
            continue
        if path.stat().st_size > 2_000_000:
            issues.append(f"Unexpected large file; review provenance: {rel}")
            continue
        if path.suffix.lower() in {".md", ".py", ".yml", ".yaml", ".json", ".toml", ".txt", ".ps1", ".sh"}:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for pattern in SECRET_PATTERNS:
                if pattern.search(text):
                    issues.append(f"Potential secret pattern in {rel}")
                    break
    # Detect documentation that points to known critical paths which are absent.
    readme = root / "README.md"
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        for required in ("scripts/fitness_manager.py", "scripts/audit_release.py", "tests"):
            if required not in text:
                issues.append(f"README missing required project path reference: {required}")
            elif required == "tests" and not (root / "tests").is_dir():
                issues.append("README references tests/ but directory is missing")
            elif required != "tests" and not (root / required).exists():
                issues.append(f"README references missing path: {required}")
    return issues


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args(argv)
    issues = audit(Path(args.root))
    if issues:
        print("RELEASE AUDIT: FAIL")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("RELEASE AUDIT: PASS (hygiene checks only; not a security certification)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
