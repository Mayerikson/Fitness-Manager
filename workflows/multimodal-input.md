# Multimodal Input Workflow

## Trigger
Use when the user submits text or audio to record a measurement, food, workout, or run.

## Required flow
1. Authenticate the channel/user before processing.
2. For audio, enforce size/duration limits and transcribe locally when available.
3. Display the recognized transcript to the user.
4. Parse only supported fields and validate units/ranges.
5. Display a structured preview, including uncertainties and missing fields.
6. Ask for explicit confirmation.
7. Persist only after confirmation and preserve source provenance.
8. Report the resulting record ID.

## Do not
- Save health records from unconfirmed audio/transcript.
- Guess unclear numbers, units, dates, exercise variations, or nutrition values.
- Silently use cloud transcription or cloud LLMs.
- Retain raw audio after local transcription by default.
- Treat a transcript as proof that the user approved the interpretation.

## Correction
If a field is wrong, request corrected text or a new audio message. Keep the original pending event rejected/cancelled and create a new event; never silently rewrite a confirmed historical record.
