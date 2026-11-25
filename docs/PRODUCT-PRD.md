# Product Requirements Document - Fitness Manager

## Product vision

Provide an affordable, local-first system that helps an individual plan and execute resistance training, nutrition habits, body measurements, and road running up to 15 km. The product should reduce friction for people who cannot afford continuous personal coaching.

## Primary beta user

The first beta is a single user. The public repository contains no personal profile or health records. Multi-user operation is out of scope until privacy, authentication, authorization, and data isolation are designed and tested.

## Core user journeys

1. Open the daily plan and understand what to do.
2. View an exercise demonstration and safety cues.
3. Replace an unavailable exercise with a biomechanically appropriate alternative.
4. Record the work actually completed.
5. Log food with quantities and preparation details.
6. Record weight, waist, and other measurements.
7. Log walking or running sessions up to the 15 km ceiling.
8. Review progress and understand why a plan change is proposed.
9. Export, back up, and restore personal records.
10. Submit text or audio in natural language, review the system's interpretation, correct it if needed, and explicitly confirm before saving.
11. Use the local system without connecting an LLM for routine records, calculations, history, and supported speech transcription.

## Functional requirements

- Portable `SKILL.md` entry point and internal `MODULE.md` modules.
- Dynamic routing to training, nutrition, progress, running, evidence, and quality workflows.
- SQLite local history with append-preserving records and audit events.
- Verified local backups and authenticated encrypted cloud copies.
- Exercise substitution ranked by movement pattern, equipment, target muscles, constraints, and user skill.
- Contingency flows for crowded gyms, limited time, illness, and injury; illness or injury must not trigger unsafe substitute workouts.
- Food flexibility for budget, preferences, travel, celebrations, and changing availability.
- Training progression based on adherence, technique, performance, recovery, and user approval, not calendar alone.
- Running progression capped at 15 km.
- Explainable decisions with source, uncertainty, approval state, and review date.
- Multimodal ingestion for text and audio, with mandatory preview and user confirmation before domain writes.
- Optional local speech-to-text using a locally executed model; no paid transcription API required.
- Local deterministic interpretation for supported record types; ambiguous transcripts are rejected or returned for correction rather than guessed.
- Audio minimization: process from temporary storage, delete the original after transcription, and retain only the minimum transcript/provenance required for a pending or confirmed event.

## Non-functional requirements

- Local-first and usable without a paid API.
- Model/provider independent data layer.
- Offline access to previously stored plans and records.
- Minimal dependencies.
- Explicit privacy boundaries.
- Reproducible tests and release hygiene.
- No silent modification of training, nutrition, or personal data.
- No required LLM for CRUD, text parsing, supported audio transcription, validation, confirmation, or local reporting.
- Model-independent ingestion contract shared by Telegram and the future PWA/mobile client.

## Out of scope for the single-user beta

- Medical diagnosis or treatment.
- Autonomous clinical prescriptions.
- Social feeds or public health profiles.
- Advertising and monetization.
- Multi-user cloud database and account system.
- Automatic video downloads from third-party platforms.

## Success measures

- Workout completion rate.
- Successful exercise substitutions.
- Time required to start and finish a workout.
- Consistency of food and measurement logging.
- Data integrity and successful backup restoration.
- User understanding of plan changes.
- Retention and repeated weekly use.


## Implementation status note
The current beta implements local data capture and basic reporting. PWA screens, multi-user capabilities, autonomous LLM agents, scheduled backups, and Supabase sync remain roadmap items. Agent Markdown files are role instructions, not executable background agents.

## Multimodal input and mobile roadmap

Text and audio are equal input modes. The system must show the recognized text and structured interpretation (event type, values, units, date, and source) before a user confirms. Confirmation is an explicit action; no speech transcript alone may write a domain record. The initial Telegram voice adapter uses local faster-whisper when installed. The PWA will capture audio in the browser and submit it to an authenticated local service for transcription where possible. If the local service is unreachable, the PWA may queue the encrypted/temporary input locally for later processing; it must not silently send audio to a cloud service. Cloud transcription requires a separate, explicit opt-in and is not part of the default product.

Mobile data must not write directly to a desktop SQLite file. A future authenticated API will accept idempotent events and synchronize them with the local source of truth. Offline mobile capture will use a local queue (e.g. IndexedDB) and explicit conflict handling.
