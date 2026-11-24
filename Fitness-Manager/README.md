# Fitness Manager

A local-first, model-portable fitness assistant for resistance training, nutrition tracking, body measurements, and road running up to 15 km.

**Status:** personal beta / handoff candidate. This is not a medical device, clinical decision system, or substitute for qualified professionals.

## Product principles

- **Local-first:** personal records live in SQLite on the user's device.
- **Model-independent:** the knowledge and data layers do not depend on one AI provider.
- **Cost-conscious:** no paid API or hosted database is required for local logging, calculations, or backups.
- **Bounded workflows:** invoke only the specialist workflow required for the current task.
- **Explainable changes:** recommendations record inputs, rationale, uncertainty, approval, and review criteria.
- **Safe by default:** personal health data and private course material are excluded from the public repository.

## Quick start

Requirements: Python 3.9 or later. Optional encrypted Google Drive backups require the dependency in `requirements-backup-encryption.txt`.

### Windows

```powershell
python .\scripts\fitness_manager.py init
python .\scripts\fitness_manager.py report
powershell -ExecutionPolicy Bypass -File .\install.ps1 -ClaudeCode
```

### macOS / Linux

```bash
python3 scripts/fitness_manager.py init
python3 scripts/fitness_manager.py report
bash install.sh --codex
```

See `adapters/` for host-specific installation notes. A model provider is not automatically a Skill runtime: DeepSeek, for example, must be used through an agent host that can load files and run local scripts.

## Local data and privacy

The default database is stored outside the repository:

- Windows: `%USERPROFILE%\.fitness-manager\fitness_manager.sqlite`
- macOS / Linux: `~/.fitness-manager/fitness_manager.sqlite`

The user's profile, health measurements, food logs, workouts, runs, backups, and configuration must remain outside the Git checkout. See `.gitignore` and `governance/evidence-hygiene/MODULE.md`.

Initialize and inspect the local history:

```bash
python scripts/fitness_manager.py init
python scripts/fitness_manager.py report
python scripts/fitness_manager.py history --limit 50
```

Record examples using synthetic values only:

```bash
python scripts/fitness_manager.py weigh-in --weight 73.4 --date 2025-01-10
python scripts/fitness_manager.py measure --kind waist --value 84 --unit cm --date 2025-01-10 --method "horizontal at navel"
python scripts/fitness_manager.py workout --date 2025-01-10 --session A --exercise "Example exercise" --sets 2 --reps 12 --load-kg 10 --rir 3
python scripts/fitness_manager.py run --date 2025-01-11 --distance-km 3 --duration-min 24 --rpe 4
```

These examples are test data, not fitness recommendations.

## Backup and restore

Create and verify a local backup:

```bash
python scripts/fitness_manager.py backup
```

Backups are stored in the user's private data directory, include SHA-256 manifests, and are checked with SQLite integrity validation. SHA-256 detects accidental corruption; it is not a digital signature and does not protect against a privileged local attacker.

For encrypted Google Drive desktop sync, install the optional dependency and configure a local passphrase in the process environment. Never put credentials or passphrases in source control. The app blocks cloud copies when encryption is unavailable or no passphrase is configured. A local synced folder is not proof that Google Drive has finished uploading; verify sync status in the Drive client.

Restore only from a verified backup:

```bash
python scripts/fitness_manager.py restore --from "PATH_TO_BACKUP"
```

The restore process creates a pre-restore safety copy. Read the security documentation before enabling cloud backup.

## Repository map

- `SKILL.md`: portable Fitness Manager entry point.
- `agents/`: specialist role prompts, invoked only when needed.
- `workflows/`: bounded task workflows.
- `governance/`: internal `MODULE.md` contracts, including MYK integration.
- `scripts/`: local SQLite CLI and release hygiene checks.
- `tests/`: automated tests using synthetic data.
- `adapters/`: host-specific installation and compatibility notes.
- `course-library/`: instructions for keeping private course files locally; no course files are distributed.
- `templates/`: blank tracker workbook, without personal measurements.
- `docs/`: product, architecture, security, and handoff documents.
- `spec/`: product specifications and decision artifacts.

## Course material and third-party references

The public repository intentionally excludes the user's Leandro Twin course PDFs, spreadsheets, exercise tables, and extracted transcriptions. Keep lawfully obtained personal copies in a private local directory as described in `course-library/README.md`. Do not redistribute course materials without permission from the rights holder.

Humanizer and Claude-BugHunter are referenced as methodological inspiration only. Their code and payloads are not bundled. See `references/THIRD_PARTY_INSPIRATION.md`.

The MYK SPEC project is maintained separately at https://github.com/Mayerikson/Spec. This repository includes only a governance bridge; it does not bundle the MYK source package. See `governance/MODULE.md`.

## Development and quality checks

```bash
python -m unittest discover -s tests -v
python scripts/audit_release.py .
```

The release audit is a hygiene check, not a complete SAST, dependency scanner, penetration test, or independent security certification. See `CONTRIBUTING.md`, `SECURITY.md`, and `docs/HANDOFF.md`.

## License status

No open-source license has been selected yet. Until a license is added, the default copyright rules apply; public visibility does not grant permission to reuse, modify, or redistribute the code. See `LICENSE-STATUS.md`.
