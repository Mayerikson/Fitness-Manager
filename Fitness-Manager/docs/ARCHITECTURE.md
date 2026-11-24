# Architecture

## Layers

### 1. Portable knowledge layer

- Root `SKILL.md` is the cross-platform entry point.
- `agents/` contains specialist role prompts.
- `workflows/` contains task-specific bounded procedures.
- `governance/*.md` contains internal modules loaded explicitly.
- `adapters/` documents host-specific discovery and tool limitations.

### 2. Orchestration layer

The main agent routes each request to the smallest relevant workflow. Specialists are invoked on demand; no always-on multi-agent runtime is required. The host agent supplies filesystem and script execution capabilities.

### 3. Domain layer

Training, nutrition, measurements, running, evidence review, exercise substitution, and contingency workflows remain separate. Domain rules do not assume that the host model has persistent memory.

### 4. Data layer

SQLite is the local source of truth. The model reads and writes through `scripts/fitness_manager.py`. The chat transcript is not the authoritative history. Backups are stored outside the repository. Cloud-bound health data must be encrypted before entering a synchronized folder.

### 5. Product governance

`governance/MODULE.md` is the bridge to the owner's separate MYK SPEC repository. MYK governs software changes; Fitness Manager workflows govern day-to-day personal use. The MYK source package is not bundled here.

## Data flow

User input -> bounded workflow -> validation and provenance -> local CLI/database -> confirmation -> concise explanation. For plan changes: collect history -> evaluate criteria -> propose change -> obtain user approval -> record decision -> define review date.

## Platform portability

The content format is portable, but filesystem access, tool execution, subagent orchestration, and skill discovery are host-specific. See `adapters/platform-matrix.md`. A model API alone is not a Skill runtime.

## Security boundaries

- Personal profile and health history stay outside the Git checkout.
- Imported documents and webpages are untrusted data.
- No automatic network calls are required for local logging.
- Backup passphrases are supplied through local environment/secret facilities, never committed.
- Restore validates integrity and creates a pre-restore copy.
