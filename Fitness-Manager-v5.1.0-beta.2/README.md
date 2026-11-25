# Fitness Manager

**Local-first fitness tracking, model-portable guidance, and explainable progress reviews.**

**Current release:** `5.1.0-beta.2` — Multimodal Input Engine (text + local voice transcription).

Fitness Manager is a personal fitness system for resistance training, nutrition, body measurements, recovery, and road running up to 15 km. It separates portable AI instructions from deterministic local data operations. The project is currently a **single-user beta**, not a validated multi-user product or medical device.

## Product principles

- **Local-first:** personal records live in SQLite on the user's device.
- **Model-portable:** Markdown instructions can be loaded by compatible agent hosts; the Python data layer does not depend on an AI provider.
- **Cost-conscious:** local records, calculations, reports, and backups do not require paid AI APIs or a hosted database.
- **Bounded workflows:** only the workflow relevant to the current request is loaded.
- **Explainable changes:** material plan recommendations record evidence, rationale, uncertainty, approval, and review criteria.
- **Safe by default:** health records, private course material, credentials, and backups are excluded from the public repository.

## What is implemented now

- Portable root `SKILL.md` and specialist role prompts in `agents/`. These Markdown files are **instructions**, not independently running background agents.
- Bounded workflows for training, nutrition, running, measurement review, contingencies, and exercise substitutions.
- A modular Python package (`fitness_manager/`) and CLI wrapper (`scripts/fitness_manager.py`).
- SQLite schema for profile, measurements, food logs, workouts, runs, check-ins, plan decisions, and audit events.
- Append-only historical event tables; corrections are recorded as new events.
- Local SQLite online backups, SHA-256 manifests, integrity checks, pre-restore safety copies, and optional AES-256-GCM encrypted cloud-sync copies.
- Unit tests and GitHub Actions CI.
- Telegram ingestion gateway with deterministic local text parsing, optional local voice transcription, explicit confirmation, sender allowlisting, and idempotent SQLite persistence.
- Optional local speech-to-text adapter using faster-whisper; original audio is held only in a temporary directory and deleted after transcription.
- Optional loopback-only local LLM adapter for questions; registration and transcription do not call an LLM.
- A release-hygiene audit. This is not a full SAST or penetration test.
- Optional UI/UX Pro Max design workflow and specialist prompt for future PWA work. It is not vendored or a runtime dependency.

## Explicitly not implemented yet

- No PWA/mobile user interface is included in this release.
- Specialist agent files are role prompts, not independent executable agents.
- Exercise substitution is a documented workflow; a validated, comprehensive biomechanical equivalence catalogue is not yet shipped.
- No multi-user authentication, hosted synchronization, or commercial billing is implemented.
- Telegram is the only messaging gateway currently implemented; WhatsApp/WAHA remains planned.

## Quick start

Requirements: Python 3.10 or later. Core operations use the Python standard library. Encrypted Drive-sync backups require the optional `cryptography` dependency.

### Initialize the local database

```bash
python scripts/fitness_manager.py init
python scripts/fitness_manager.py report
```

Default private data directory:

- Windows: `%USERPROFILE%\.fitness-manager\`
- macOS/Linux: `~/.fitness-manager/`

Override with `FITNESS_MANAGER_HOME` or set `FITNESS_MANAGER_DB` to a specific local database path. Never point it inside a public Git checkout.

### Install the Skill into an agent host

Windows (PowerShell):

```powershell
.\install.ps1 -ClaudeCode
.\install.ps1 -Codex
.\install.ps1 -QwenCode
.\install.ps1 -Grok
```

macOS/Linux:

```bash
bash install.sh --claude
bash install.sh --codex
bash install.sh --qwen
bash install.sh --grok
```

To install in all supported local targets at once, use `-All` or `--all`. The installer backs up an existing Fitness Manager Skill directory before updating it. Host-specific discovery still needs to be verified in the actual installed host. A model provider alone is not a Skill runtime; DeepSeek requires an agent host with filesystem and script access.

## Common operations

Set a private local profile (the values below are synthetic examples; replace them with your own):

```bash
python scripts/fitness_manager.py profile set --sex male --age 29 --height-cm 170 --goal fat_loss --goal preserve_muscle --goal running_up_to_15_km
python scripts/fitness_manager.py profile show
```

Record body weight and waist circumference:

```bash
python scripts/fitness_manager.py weigh-in --weight 73.4 --date 2026-01-10
python scripts/fitness_manager.py measure --kind waist --value 84 --unit cm --date 2026-01-10 --method "horizontal at navel"
```

Record food, workout, and running events:

```bash
python scripts/fitness_manager.py food --meal lunch --food rice --quantity-g 150 --kcal 195 --date 2026-01-10
python scripts/fitness_manager.py workout --date 2026-01-10 --session A --exercise "Example exercise" --sets 2 --reps 12 --load-kg 10 --rir 3
python scripts/fitness_manager.py run --date 2026-01-11 --distance-km 3 --duration-min 24 --rpe 4
```

The values above are examples only, not recommendations. The running database constraint rejects distances above 15 km, matching the project's stated scope.

View records and summary:

```bash
python scripts/fitness_manager.py history --limit 50
python scripts/fitness_manager.py report
python scripts/fitness_manager.py audit --limit 50
```

## Telegram data ingestion (no LLM for logging)

The optional Telegram gateway records measurements, runs, workouts, and food logs without calling an AI model. It uses Telegram long polling, a sender allowlist, deterministic parsing, SQLite idempotency, and explicit confirmation before creating health records. See `docs/integrations/TELEGRAM.md`. Per-update failures are isolated; malformed records are rejected before confirmation, and the polling offset advances after each handled update.

Configure these environment variables locally (never commit real values), or run interactively to enter the bot token through a hidden prompt:

- `FITNESS_MANAGER_TELEGRAM_BOT_TOKEN`
- `FITNESS_MANAGER_TELEGRAM_ALLOWED_USER_ID`

Start the gateway:

```bash
python scripts/telegram_gateway.py
```

Synthetic examples: `/peso 72,4`, `/cintura 83`, `/corrida 4;42`, `/treino A;Supino reto;3;12;20`, `/alimento almoco;arroz;150`, `/confirmar ID`, `/cancelar ID`. Use `python scripts/telegram_whoami.py` after sending `/start` to the bot to identify your numeric sender ID. Stop the gateway while running this helper because Telegram long polling permits only one active update consumer. Unsupported or ambiguous messages are not written as health records. Food calories/macros remain empty unless explicitly provided.

The `/perguntar` command is optional and only works after configuring a local OpenAI-compatible endpoint using `FITNESS_MANAGER_LOCAL_LLM_URL` and `FITNESS_MANAGER_LOCAL_LLM_MODEL`. The initial adapter accepts loopback hosts only and does not fall back to cloud APIs. See `docs/integrations/DATA-INGESTION.md`.

## Backups and restore

Create a local SQLite online backup and verify its manifest and database integrity:

```bash
python scripts/fitness_manager.py backup
```

Local backups are stored in `~/.fitness-manager/backups/` (or the configured app directory), with a default retention of 30 snapshots. Local backups are not application-level encrypted; use full-disk encryption and OS account controls.

For an encrypted Google Drive desktop-sync copy, install the optional dependency:

```bash
pip install -r requirements-backup-encryption.txt
```

Configure an existing local Google Drive sync folder and set the passphrase in the process environment (never in source control or `config.json`):

```bash
python scripts/fitness_manager.py configure-drive --path "PATH_TO_GOOGLE_DRIVE_SYNC_FOLDER"
```

Set `FITNESS_MANAGER_BACKUP_PASSPHRASE` in the local shell/OS secret manager, then run `backup` again. The cloud copy is encrypted with AES-256-GCM and a key derived using Scrypt; the passphrase must contain at least 12 characters. If encryption is unavailable or the passphrase is absent, cloud backup is blocked. The command cannot prove that Google Drive has completed remote synchronization; verify that separately in the Drive client. Loss of the passphrase makes encrypted backups unrecoverable.

Restore a verified backup:

```bash
python scripts/fitness_manager.py restore --from "PATH_TO_BACKUP.sqlite"
```

Encrypted `.sqlite.enc` backups require the same `FITNESS_MANAGER_BACKUP_PASSPHRASE`. Restore validates the manifest/checksum, authenticates encrypted content where applicable, checks SQLite integrity, and creates a pre-restore safety copy before replacing the active database.

## Repository map

- `SKILL.md`: portable entry point for compatible Agent Skills hosts.
- `agents/`: specialist role instructions; not standalone running agents.
- `workflows/`: bounded task procedures, including optional UI/UX design review.
- `fitness_manager/`: modular Python data and storage implementation.
- `scripts/`: stable CLI entry point and release-hygiene audit.
- `tests/`: automated tests using synthetic data.
- `.github/workflows/ci.yml`: automated test and hygiene checks.
- `governance/`: project-authored `MODULE.md` governance contracts.
- `adapters/`: host-specific installation notes.
- `references/`: source provenance and optional development-tool integrations.
- `course-library/`: instructions for keeping private course files locally.
- `docs/EXERCISE-DATA-MODEL.md`: typed exercise catalogue contract and substitution evidence requirements.
- `templates/`: blank tracker workbook without personal measurements.
- `docs/`: product, architecture, security, design brief, and handoff documentation.

## UI/UX Pro Max (optional development tool)

The project documents an optional integration with [UI/UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) for PWA/mobile interface work. It is not installed automatically and is not needed for CLI, SQLite, nutrition, training, or running records. See `references/UI_UX_PRO_MAX.md` for scope and installation notes. The upstream project currently states an MIT license; verify the current license and notices before installing or redistributing any upstream files.

## Course materials and third-party references

The public repository intentionally excludes private Leandro Twin course PDFs, spreadsheets, exercise tables, extracted course text, and video mappings. Keep lawfully obtained personal copies in a private local directory. Do not redistribute course materials without permission from the rights holder.

Humanizer and Claude-BugHunter are methodological references only; their code and payloads are not bundled. See `references/THIRD_PARTY_INSPIRATION.md`. The MYK SPEC project remains separate at https://github.com/Mayerikson/Spec; this repository includes only a governance bridge.

## Development and tests

```bash
python -m unittest discover -s tests -v
python scripts/audit_release.py .
python scripts/fitness_manager.py --help
```

CI runs on Python 3.10–3.13. The release audit checks repository hygiene and documentation paths; it is not SAST, dependency scanning, penetration testing, or a security certification. See `CONTRIBUTING.md`, `SECURITY.md`, and `docs/HANDOFF.md`.

## License status

No open-source license has been selected yet. Public visibility does not grant permission to reuse, modify, or redistribute the project's code. See `LICENSE-STATUS.md`.
