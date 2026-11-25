# Workflow — UI/UX design and review

## Trigger
A request to design, implement, review, or improve a Fitness Manager PWA/mobile interface, dashboard, chart, form, navigation, or interaction.

## Bounded procedure
1. Confirm the requested interface and the existing frontend stack.
2. Read `docs/DESIGN-SYSTEM-BRIEF.md` and `agents/uiux-agent.md`.
3. If UI/UX Pro Max is available in the current host, query only the relevant design domains and stack guidance. Do not install it automatically. If unavailable, proceed from the project brief and label the fallback.
4. Produce or update a focused design system: semantic color, typography, spacing, component, and state tokens.
5. Design the primary journey and empty/loading/offline/saved/error states.
6. Check touch targets, contrast, keyboard navigation, screen-reader semantics, reduced motion, and narrow mobile layouts.
7. Preserve business logic and existing component conventions. Avoid a parallel design system.
8. Run relevant UI tests or visual checks. Mark checks NOT_RUN when no frontend exists or no browser/device test was performed.
9. Summarize changed files, design decisions, test evidence, and remaining gaps.

## Cost and privacy
- No API call is required for the project-owned design brief.
- UI/UX Pro Max is optional and uses local search after installation; installing/updating it may require internet access.
- Do not add analytics or telemetry to the personal beta.
