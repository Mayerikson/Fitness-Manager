# MODULE - MYK SPEC Governance Bridge

## Purpose
Use the author's MYK Spec-Driven Intelligence as an optional engineering-governance layer for Fitness Manager product changes. This bridge governs software development, not daily exercise or nutrition decisions.

## Naming convention
Preserve the author's `MODULE.md` naming for internal modules. The root `SKILL.md` is the Fitness Manager entry point. Claude Code discovers Skills through `SKILL.md` in recognized skill directories; it does not automatically discover an arbitrary `MODULE.md`. Load this module explicitly from the root Skill or platform adapter. Do not rename `MODULE.md` to `SKILL.md`.

## External source
The MYK SPEC project is maintained separately by its author: https://github.com/Mayerikson/Spec. This repository does not bundle or redistribute the MYK source package. Clone or install it separately only when the owner has authorized access and its license/terms permit the intended use.

## Authority and limits
1. Host security policy, platform permissions, and user authorization take precedence.
2. MYK governs PRD, TechSpec, task planning, implementation, QA, independent review, and release.
3. Fitness Manager governs personal workflows: training, nutrition, running, measurements, and contingencies.
4. No module may change personal data, nutrition targets, training plans, synchronization, or security settings without appropriate authorization.
5. Missing evidence or unavailable tools must be reported as `NOT_RUN`, `BLOCKED`, or `PENDING`, never `PASS`.
6. Do not claim independent review when the same agent implemented and reviewed without a separate verification step.

## Engineering flow
Discovery -> PRD -> TechSpec -> Task Planning -> Implementation -> QA -> Independent Review -> Release.

Use proportional process for low-risk changes. Database, authentication, encryption, export, synchronization, permissions, and health-data changes require a threat review, tests, and explicit approval for material behavior changes.

## Bounded efficiency
Invoke only the modules required for the current task. Do not launch all subagents by default. Do not install tools or external dependencies without a documented need and authorization.
