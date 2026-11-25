# Developer handoff

## Current state

Fitness Manager is a single-user, local-first beta. The repository contains a portable Skill entry point, role prompts, bounded workflows, a modular Python/SQLite CLI, backup and restore operations, automated tests, CI, adapters, governance modules, and product documentation.

## Implemented versus planned

### Implemented
- SQLite schema and CLI for profile, measurements, food, workouts, runs, check-ins, and plan decisions.
- Local backup, SHA-256 manifest, SQLite integrity validation, and pre-restore safety copy.
- Optional AES-256-GCM encrypted copy for a local Google Drive desktop-sync directory.
- Append-only historical event records and basic audit triggers.
- Unit tests and GitHub Actions CI.
- Optional UI/UX Pro Max integration guidance (not vendored).
- PWA design brief; no production PWA implementation yet.

### Not implemented / not yet verified
- Native PWA or mobile application.
- Autonomous LLM subagents; agent files are role prompts.
- Automatic daily backup scheduler. Backups are currently manual.
- Supabase synchronization.
- End-to-end integration tests in every supported agent host.
- SAST, dependency vulnerability scanning, penetration testing, or independent security certification.

## Important conventions
- Keep the root entry point named `SKILL.md`.
- Preserve the author's internal `MODULE.md` naming. Claude Code discovers Skills through `SKILL.md`; arbitrary `MODULE.md` files are loaded explicitly by the root Skill or adapter.
- The MYK SPEC project remains separate at https://github.com/Mayerikson/Spec.
- Do not bundle private course PDFs, spreadsheets, exercise tables, extracted course text, personal profiles, databases, or backups.
- UI/UX Pro Max is an optional development-time tool; do not make it a runtime dependency.

## First-run checklist
1. Install Python 3.10+.
2. Run `python scripts/fitness_manager.py init`.
3. Set the private profile with `python scripts/fitness_manager.py profile set ...`.
4. Run `python scripts/fitness_manager.py report`.
5. Install the Skill in one host using the matching adapter.
6. Run `python -m unittest discover -s tests -v`.
7. Run `python scripts/audit_release.py .`.
8. Create a local backup and test restoration with synthetic data before entering personal data.
9. Configure encrypted Google Drive backup only after installing the optional dependency, setting a strong local passphrase, and verifying the desktop sync directory.

## Release gates
- Unit tests pass on supported Python versions.
- `scripts/audit_release.py` passes.
- No personal data, secrets, private course material, database, or backup is present.
- Backup and restore are tested with synthetic data.
- README, changelog, and code agree.
- Third-party dependencies and notices are reviewed.
