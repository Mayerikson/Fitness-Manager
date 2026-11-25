# Multimodal Input Engine

## Product decision
Text and audio are equal input modes. Both must produce a preview of the system's interpretation and require explicit confirmation before a health record is committed.

## Current implementation
- Telegram text: deterministic local parser, pending event, confirmation.
- Telegram voice/audio: optional faster-whisper local transcription, deterministic parser, transcript + structured preview, confirmation.
- Original audio: temporary directory only; deleted after processing.
- No LLM or paid transcription API is used for registration.
- Unknown/ambiguous transcripts create no health record.

## Local speech recognition
Install `requirements-audio.txt`. The default model is `base`, language `pt`, CPU `int8`. Model weights may be downloaded once and cached. After caching, inference is local. Model size, hardware and audio quality affect latency and accuracy. Configure `FITNESS_MANAGER_WHISPER_MODEL`, `FITNESS_MANAGER_WHISPER_DEVICE`, and `FITNESS_MANAGER_WHISPER_COMPUTE_TYPE`.

## Confirmation contract
The preview must show: transcript, event type, values, units, date, and source. Confirmation is a separate user action. A transcript is not equivalent to consent. Corrections should create a new pending candidate or require the user to resend corrected text; never mutate a confirmed historical record.

## PWA/mobile target (not yet implemented)
1. Capture microphone audio in the browser using a secure context.
2. Store an unsubmitted recording only in temporary browser storage.
3. Send it to an authenticated local API when the user's local service is reachable.
4. Transcribe locally on the user's computer or supported on-device runtime.
5. Return transcript and structured preview.
6. Require user confirmation in the app.
7. Persist an idempotent event in SQLite.
8. Delete temporary audio.

If offline, the PWA may queue an event in IndexedDB and retry later. It must preserve an idempotency key and must not silently use cloud transcription. A mobile device must not access the desktop SQLite file directly. Synchronization must go through an authenticated API.

## Privacy and limits
- Telegram transport still passes through Telegram infrastructure.
- The local transcription adapter limits input to 15 MB and five minutes in the Telegram gateway.
- Raw audio is not included in SQLite backups.
- Unsupported transcripts are not retained as personal health records.
- Cloud transcription requires a future explicit opt-in and separate threat review.
