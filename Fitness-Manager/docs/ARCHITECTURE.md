# Architecture

## Layers

### 1. Portable knowledge layer
- Root `SKILL.md` is the portable entry point.
- `agents/` contains role prompts; these are not autonomous running agents.
- `workflows/` contains bounded task procedures.
- `governance/` contains project-authored `MODULE.md` contracts loaded explicitly.
- `adapters/` documents host-specific discovery and limitations.

### 2. Orchestration layer
The host agent routes a request to the smallest relevant workflow. It may instantiate subagents if the host supports them, but no always-on agent runtime is required. Host discovery, filesystem permissions, and tool execution are host-specific.

### 3. Domain layer
Training, nutrition, measurements, running (up to 15 km), evidence review, exercise substitution, and contingencies remain separate. The model provides interpretation; deterministic calculations and persistence are handled by Python.

### 4. Application/data layer
The `fitness_manager/` Python package owns SQLite schema, CLI operations, backup, encryption helpers, and restore. `scripts/fitness_manager.py` is a stable entry point. SQLite is the local source of truth; the chat transcript is not. The profile and health history live outside the Git checkout.

### 5. Storage and recovery
SQLite uses foreign keys, WAL, constraints, and an append-only event model for historical records. Local snapshots use SQLite's online backup API, SHA-256 manifests, and integrity checks. Optional cloud-sync copies are encrypted with AES-256-GCM using a Scrypt-derived key. The app cannot verify that the desktop sync client has completed remote synchronization.

### 6. Product governance
`governance/MODULE.md` bridges to the owner's separate MYK SPEC repository. `governance/quality-gates/MODULE.md` applies proportional checks; `governance/evidence-hygiene/MODULE.md` controls personal data. MYK governs product/code changes; Fitness Manager workflows govern personal use.

### 7. Optional UI/UX development intelligence
`references/UI_UX_PRO_MAX.md` documents the optional upstream UI/UX Pro Max Skill for future PWA/mobile design. It is not vendored, installed automatically, or required by the data layer.

## Data flow
User input -> bounded workflow -> provenance and validation -> Python CLI -> SQLite -> confirmation -> concise explanation. For plan changes: read history -> evaluate criteria -> propose change -> obtain user approval -> append a decision -> define review date.

## Security boundaries
- Personal profile, database, backups, exports, and passphrases stay outside the Git checkout.
- Imported documents and webpages are untrusted data.
- Local logging does not require network access.
- Cloud-bound health data must be encrypted before entering a synchronized folder.
- SHA-256 detects accidental corruption; authenticated encryption protects encrypted backup contents. Neither protects a compromised endpoint or a privileged administrator.
- Restore validates backup authenticity/integrity and creates a pre-restore safety copy.


## Data Integration Engine

The Telegram-first gateway is an optional input adapter. It authenticates a single allowlisted sender, parses a deliberately limited command grammar without an LLM, creates pending ingestion events, and writes domain records only after explicit confirmation. Idempotency is enforced by a unique `(source, external_event_id)` key. Telegram polling offsets are persisted in SQLite. The optional question path uses a loopback-only OpenAI-compatible local model endpoint and has no cloud fallback. See `docs/integrations/`.
