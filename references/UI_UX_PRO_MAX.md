# Optional UI/UX Pro Max integration

## Decision
Use `nextlevelbuilder/ui-ux-pro-max-skill` as an **optional development-time design tool** for the future PWA and mobile experience. It is not a runtime dependency of the Fitness Manager data layer and is not invoked for ordinary food, workout, measurement, or run logging.

Upstream: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
License stated by upstream: MIT. Review the current upstream LICENSE and notices at the time of installation or redistribution.

## Why it fits
The upstream project provides searchable local design guidance, stack-specific recommendations, design-system generation, and UX/accessibility checks. Its README states that the Python search scripts use the standard library and do not make network calls during searches. Initial installation/update may require internet access and Node/npm or the Skills installer depending on the selected method.

## Optional installation
For an agent host supporting Agent Skills CLI:

```bash
npx skills add nextlevelbuilder/ui-ux-pro-max-skill --skill ui-ux-pro-max
```

For Claude Code, follow the current upstream marketplace instructions in its README. Do not assume that a skill installed in one host is automatically available in another.

## Fitness Manager usage contract
Invoke only for:
- PWA/mobile screen design and implementation;
- workout-mode interaction design;
- dashboard, charts, forms, navigation, responsive layouts;
- accessibility and usability review.

Do not invoke for:
- SQLite CRUD, backup/restore, or migrations;
- nutrition calculations;
- training prescription or exercise equivalence decisions;
- ordinary progress logging.

## Design-system requirements
- Mobile-first, usable one-handed during gym sessions.
- Large touch targets, clear contrast, keyboard and screen-reader support.
- Minimize time-to-action: show today's session and next action without forcing chat.
- Offline-first for previously loaded plans and local logging.
- Avoid ad-heavy, dark-pattern, or engagement-maximizing patterns.
- Never expose private health data in design screenshots or fixtures.
- Preserve semantic tokens and existing component conventions; do not create a parallel theme system without a documented reason.

## Bounded efficiency
Keep this dependency optional. Pin a reviewed upstream release/commit for reproducible design work. Do not vendor the upstream repository into this project unless there is a specific need and all license notices are retained.
