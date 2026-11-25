# Fitness Manager — UI/UX design brief

**Status:** design input for the future PWA; no production UI is implemented yet.

## Product context

The product serves people with limited budgets who want to train independently, understand exercise execution, record food and activity, and see progress without paying for continuous coaching. The first beta user is also the product's initial usability tester.

## Primary design principle

**Open, understand the next action, complete it, record it, leave.** The interface must reduce time and cognitive load during a gym session. Chat is optional, not the primary navigation model.

## Primary journeys

1. **Today's workout:** view the session, exercise order, sets, reps, rest target, and demo link.
2. **Equipment unavailable:** mark the exercise as occupied and choose from ranked alternatives with an explanation of equivalence and differences.
3. **Set logging:** enter load/reps/RIR with large touch controls and minimal typing.
4. **Workout completion:** show what was completed, skipped, or substituted and confirm that records were saved locally.
5. **Food logging:** quickly record common meals, quantities, preparation state, and uncertainty in nutrition estimates.
6. **Progress review:** compare dated weight/waist measurements and training/running trends without implying that estimates are clinical measurements.
7. **Offline use:** open previously loaded plans, exercise instructions, and local records without a network connection.

## UX requirements

- Mobile-first and one-handed use during training.
- Large touch targets, readable typography, clear focus states, and high contrast.
- No forced chat flow for routine tasks.
- Minimal steps to start or resume a workout.
- Clear distinction between measured, user-reported, calculated, estimated, and missing data.
- Explicit saved/error/offline states; never imply persistence before the local database confirms success.
- Accessible labels, keyboard navigation, screen-reader semantics, and reduced-motion support.
- Avoid shame-based language, streak pressure, dark patterns, invasive ads, and manipulative engagement loops.
- Make rest, recovery, and stopping for symptoms first-class options.

## Initial information architecture

- **Today:** next workout, quick actions, current plan status.
- **Train:** workout session, exercise detail, alternatives, rest timer, set logging.
- **Nutrition:** meal log, daily summary, flexible substitutions.
- **Run:** walking/running log and progression capped at 15 km for this product configuration.
- **Progress:** weight, measurements, strength, adherence, and trends.
- **History:** searchable personal records and decision log.
- **Settings:** backup status, export, privacy, and data controls.

## Visual direction

Use UI/UX Pro Max as an optional design-research aid to select a restrained, accessible visual system appropriate for a fitness utility. Prefer functional clarity over a generic bodybuilding aesthetic. Establish semantic design tokens for color, type, spacing, radii, elevation, and interaction states. Do not copy a third-party product's branding.

## Data and privacy

- Local-first by default.
- No third-party analytics in the personal beta.
- Do not display sensitive health information on lock-screen notifications.
- Use synthetic data in screenshots and UI tests.
- Backup/export actions must explain destination and encryption status.

## Acceptance criteria for first PWA prototype

- A user can open today's workout and begin without asking an AI model.
- Each exercise has an instruction/demo path and an equipment-unavailable path.
- A completed set is persisted locally and survives app reload/offline restart.
- The user can record a food item and a body measurement offline.
- The UI visibly distinguishes saved, pending, failed, and unsynced states.
- Core flows work at narrow mobile widths and with keyboard/screen-reader navigation.
- No private data is present in fixtures, screenshots, or repository artifacts.
