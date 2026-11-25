# Data Integration Engine

## Purpose

Provide a deterministic, model-independent ingestion pipeline for local and messaging inputs.

## Pipeline

1. Receive an input from a trusted channel.
2. Authenticate the sender and enforce channel scope.
3. Normalize the payload.
4. Parse only supported, explicit formats.
5. Validate domain constraints (including the 15 km running scope).
6. Persist an idempotent pending event.
7. Ask the user to confirm.
8. Atomically create the domain record and mark the event confirmed.
9. Record an audit event and report the local record ID.

## Bounded efficiency

- Logging commands use deterministic Python only.
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

## Future adapters

WhatsApp is intentionally not implemented in this release. A future WAHA adapter must use the same ingestion contract, verify sender identity, authenticate webhook requests, restrict network exposure, and preserve the same idempotency and confirmation rules. WAHA is unofficial WhatsApp Web automation and carries account and operational risks; prefer the official Meta WhatsApp Business Platform for production use.

## Pipeline design provenance

The staged ingestion, persistence-before-acknowledgement, idempotency, and explicit blocking patterns are informed by the repository owner's `digisystem-jobs-engine` project. This is an architectural adaptation, not a code import. The public repository exposes a pipeline script, pre-publication persistence tests, publisher-blocking tests, availability tests, and workflow automation; see https://github.com/Mayerikson/digisystem-jobs-engine.
