# Roadmap

## Beta 1 - Personal reliability
- Stabilize the modular SQLite CLI and schema migration path.
- Expand backup, encryption, restore, and retention tests.
- Validate the first agent host end to end.
- Validate the exercise catalog privately against the user's course files.
- Test one supported local agent end to end.

## Beta 2 - Gym mode
- Mobile-first workout screen.
- Exercise demonstrations and safety cues.
- Three to four ranked substitutions where genuinely equivalent.
- Rest timer, set logging, and workout completion.
- Offline access to previously cached plans and authorized media.

## Beta 3 - Adaptive planning
- Weekly progress review.
- Training progression and deload criteria.
- Nutrition flexibility and event handling.
- Walking/running progression capped at 15 km.
- Explainable and user-approved plan changes.

## Beta 4 - PWA
- Apply the optional UI/UX Pro Max design intelligence and establish a project-owned design system.
- Installable responsive web application.
- Offline-first UI and local persistence.
- Safe import/export and backup status.

## Beta 5 - Multi-user product research
- Threat model and privacy impact assessment.
- Authentication, authorization, tenant isolation, deletion/export.
- Cloud synchronization and conflict resolution.
- Pricing and sustainability research.

Do not build multi-user cloud infrastructure or monetization before the single-user beta proves useful and reliable.


## 5.1 — Multimodal input
- Text and audio are equal input modes, both requiring preview and confirmation.
- Telegram voice transcription is implemented as an optional local adapter.
- PWA/mobile microphone capture, IndexedDB offline queue, and authenticated local API are specified but not yet implemented.
- No cloud transcription or paid LLM is required for routine supported registrations.


## Exercise catalogue

Before enabling automatic substitutions, implement and validate the typed data contract in `docs/EXERCISE-DATA-MODEL.md`. The current substitution workflow is guidance, not a complete biomechanical equivalence engine.
