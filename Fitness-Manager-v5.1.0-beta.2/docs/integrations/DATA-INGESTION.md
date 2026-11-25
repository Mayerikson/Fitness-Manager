# Data Integration Engine

## Purpose

Provide a deterministic, model-independent ingestion pipeline for local and messaging inputs.

## Pipeline

1. Receive text or audio from a trusted channel.
2. Authenticate the sender and enforce channel scope before downloading media.
3. For audio, enforce file-size/duration limits and transcribe locally from temporary storage.
4. Delete the original audio after transcription; do not retain raw media by default.
5. Normalize the text/transcript and parse only supported, explicit formats.
6. Validate domain constraints (including the 15 km running scope).
7. Persist an idempotent pending event with minimal provenance.
8. Show the transcript and structured interpretation to the user.
9. Ask for explicit confirmation or cancellation.
10. Atomically create the domain record and mark the event confirmed.
11. Record an audit event and report the local record ID.

## Bounded efficiency

- Logging commands use deterministic Python only.
- Supported audio transcription uses optional local faster-whisper; it does not call an LLM or paid transcription API.
- Audio interpretation is a deterministic parser after transcription; unknown/ambiguous text requires correction.
- No model is called for CRUD, parsing, validation, confirmation, or reporting.
- Local LLM calls are explicit via `/perguntar` and require a loopback OpenAI-compatible endpoint.
- Unknown messages do not trigger a model call automatically.
- Food calories and macros are never inferred by the ingestion parser.

## Reliability controls

- Unique source/event key for idempotency.
- Pending confirmation before domain writes.
- SQLite transaction for confirmation and state transition.
- Persistent Telegram update offset.
- Unsupported messages remain distinguishable from valid pending records.
- No sensitive message body is written to application logs.

## Multimodal/mobile contract

All input channels must produce the same normalized event envelope: source, external event ID, sender identity, received timestamp, modality, transcript/text, parser version, parsed payload, and confirmation state. Raw audio must be temporary and excluded from backups unless a future explicit retention feature is added with consent. The PWA will use microphone capture plus an authenticated local API; offline capture may queue pending events in IndexedDB. Mobile clients must not open or modify the desktop SQLite file directly.

## Future adapters

WhatsApp is intentionally not implemented in this release. A future WAHA adapter must use the same ingestion contract, verify sender identity, authenticate webhook requests, restrict network exposure, and preserve the same idempotency and confirmation rules. WAHA is unofficial WhatsApp Web automation and carries account and operational risks; prefer the official Meta WhatsApp Business Platform for production use.

## Pipeline design provenance

The staged ingestion, persistence-before-acknowledgement, idempotency, and explicit blocking patterns are informed by the repository owner's `digisystem-jobs-engine` project. This is an architectural adaptation, not a code import. The public repository exposes a pipeline script, pre-publication persistence tests, publisher-blocking tests, availability tests, and workflow automation; see https://github.com/Mayerikson/digisystem-jobs-engine.
