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


### 8. Multimodal input layer (v5.1)
Text and audio are first-class input channels. Telegram voice/audio messages are downloaded only after private-chat sender allowlisting and size/duration checks. The audio file is written to a temporary directory, transcribed by the optional `faster-whisper` local adapter, and deleted when the temporary directory closes. The deterministic Portuguese parser converts supported transcripts into a pending event. The bot displays both the transcript and parsed candidate; only an explicit `/confirmar ID` creates the domain record. If transcription or parsing fails, no health record is written. The original audio is not retained.

The PWA/mobile target will use browser microphone capture and an authenticated local API. The local service performs transcription and parsing; the browser displays the transcript and structured preview and requires confirmation. When offline, the PWA may queue an event locally and submit it after reconnection. The desktop SQLite database is not directly shared with mobile clients; an API and idempotent event synchronization layer mediate writes.

### 9. Local processing and provider boundaries
Routine CRUD, supported text parsing, supported audio transcription, calculations, validation, confirmation, and local reporting do not call an LLM. faster-whisper is an optional local dependency; its model weights may need an initial download and can then be cached for offline inference. Local interpretation remains deterministic and deliberately bounded. An optional local LLM may answer explicit questions but is not used to decide whether a health record should be committed. Cloud AI/transcription is disabled by default and would require explicit opt-in.
