#!/usr/bin/env python3
"""Release hygiene audit for Fitness Manager; stdlib only, not a full security scanner."""
from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
errors: list[str] = []
checked = 0

FORBIDDEN_NAMES = {
    "profile.json", "config.json", ".env", "id_rsa", "id_ed25519",
    "credentials.json", "secrets.json"
}
FORBIDDEN_SUFFIXES = (".sqlite", ".sqlite3", ".db-wal", ".db-shm", ".sqlite.enc", ".pem", ".key")
SECRET_PATTERNS = [
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(rb"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    re.compile(rb"\bsk-[A-Za-z0-9_-]{24,}\b"),
    re.compile(rb"\bAIza[0-9A-Za-z_-]{30,}\b"),
]

if not (ROOT / "SKILL.md").is_file():
    errors.append("SKILL.md raiz ausente")
if not (ROOT / "governance" / "MODULE.md").is_file():
    errors.append("governance/MODULE.md ausente; preservar convencao MODULE.md")
if not (ROOT / "governance" / "quality-gates" / "MODULE.md").is_file():
    errors.append("MODULE de quality-gates ausente")
if not (ROOT / "governance" / "evidence-hygiene" / "MODULE.md").is_file():
    errors.append("MODULE de evidence-hygiene ausente")

# Public-release exclusions: course files and private MYK source stay outside this repo.
for forbidden_dir in ("source-materials", "governance/MYK-Spec-Driven-Intelligence-v2.0.0"):
    if (ROOT / forbidden_dir).exists():
        errors.append(f"diretorio nao distribuivel presente: {forbidden_dir}")
for forbidden_file in ("references/PROGRAMAS_DAS_PLANILHAS.md", "references/TEXTOS_DOS_PDFS.md", "references/INVENTARIO_FONTES.md"):
    if (ROOT / forbidden_file).exists():
        errors.append(f"transcricao de material de curso nao distribuivel: {forbidden_file}")

for path in ROOT.rglob("*"):
    if not path.is_file() or any(part in {".git", "__pycache__", ".venv", "venv"} for part in path.parts):
        continue
    checked += 1
    name = path.name.lower()
    rel = path.relative_to(ROOT).as_posix().lower()
    if name in FORBIDDEN_NAMES and not rel.endswith("data/profile.example.json"):
        errors.append(f"arquivo privado/configuracao proibido no pacote: {rel}")
    if name.endswith(FORBIDDEN_SUFFIXES):
        errors.append(f"arquivo de banco/segredo proibido no pacote: {rel}")
    if name.endswith(".sqlite") or name.endswith(".sqlite3") or name.endswith(".db"):
        errors.append(f"banco de dados encontrado no pacote: {rel}")
    if path.suffix.lower() in {".md", ".py", ".json", ".toml", ".yml", ".yaml", ".txt", ".ps1", ".sh"}:
        try:
            raw = path.read_bytes()
        except OSError as exc:
            errors.append(f"nao foi possivel ler {rel}: {exc}")
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(raw):
                errors.append(f"possivel segredo encontrado em {rel}")
                break

if errors:
    print("FAIL — auditoria de release")
    for item in errors:
        print(f"- {item}")
    sys.exit(1)

print(f"PASS — {checked} arquivos inspecionados; estrutura MODULE/SKILL preservada; nenhum artefato privado ou segredo conhecido detectado.")
print("LIMITACAO — esta auditoria nao substitui SAST, revisao humana, scanner de dependencias ou pentest autorizado.")
