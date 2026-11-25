# Developer handoff

## Current state

Fitness Manager 5.1.0-beta.5 is a single-user, local-first beta. The repository contains a portable Skill entry point, role prompts, bounded workflows, a modular Python/SQLite CLI, backup and restore operations, automated tests, CI, adapters, governance modules, and product documentation.

## Implemented versus planned

### Implemented
- SQLite schema and CLI for profile, measurements, food, workouts, runs, check-ins, and plan decisions.
- Local backup, SHA-256 manifest, SQLite integrity validation, and pre-restore safety copy.
- Optional AES-256-GCM encrypted copy for a local Google Drive desktop-sync directory.
- Append-only historical event records and basic audit triggers.
- 48 automated unit/regression tests and GitHub Actions CI (CI execution on the remote repository remains to be observed).
- Telegram text and voice/audio ingestion with optional local faster-whisper transcription, temporary-file cleanup, transcript preview, explicit confirmation, invalid-value rejection, per-update error isolation, and persistent offset advancement.
- Optional UI/UX Pro Max integration guidance (not vendored).
- PWA design brief; no production PWA implementation yet.

### Not implemented / not yet verified
- Native PWA or mobile application; only the Telegram voice adapter is implemented, while browser microphone capture and the mobile API remain planned.
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


## v5.1 multimodal input update
The beta now supports Telegram voice/audio ingestion through optional local faster-whisper transcription. It previews the transcript and structured event and requires `/confirmar ID` before saving. The raw audio is temporary and deleted. Install `requirements-audio.txt` and allow the model weights to cache on first use. PWA/mobile microphone capture, IndexedDB offline queue, and authenticated local API remain specified but not implemented.


## v5.1.0-beta.3 reliability update
- `/peso 0`, zero waist, zero sets/repetitions, and zero food quantities are rejected before confirmation.
- SQLite integrity failures during `/confirmar` are caught and the affected pending event is moved to terminal `error` status.
- Telegram updates are isolated; a failing update no longer blocks subsequent updates, and the polling offset advances per update.
- `measure` defaults to today's date when `--date` is omitted.
- The release audit now flags `__pycache__` directories instead of silently skipping them. CI removes transient caches before running the audit.
- Automatic exercise substitution remains a workflow specification, not a validated biomechanical equivalence engine.


## v5.1.0-beta.3 natural-language parser reliability
- Added regression coverage for the seven reported Portuguese phrases.
- Normalized Portuguese diacritics and peripheral punctuation before parsing.
- Generated spoken-number parsing for the 101–199 range.
- Preserved original exercise spelling and accents using source-offset mapping.
- Clarified the three-screen UX direction: Hoje, Modo Academia, and Dashboard.
