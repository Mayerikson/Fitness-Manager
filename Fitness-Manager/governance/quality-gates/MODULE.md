# MODULE — Proportional Quality Gates

## Purpose
Apply verification proportional to change risk. This module is a project-authored contract, not an auto-discovered agent.

## Gate levels
- **L0 — Personal data entry:** validate schema constraints and confirm the write succeeded. No engineering review workflow.
- **L1 — Documentation/workflow text:** check links, referenced paths, provenance, and factual consistency.
- **L2 — Application behavior:** add/update unit tests, run the full test suite, inspect the diff, and update documentation.
- **L3 — Sensitive operations:** database migrations, backup/restore, encryption, cloud sync, authentication, exports, or health-data access require threat review, negative tests, recovery tests, and explicit user approval for material behavior changes.
- **L4 — Public release:** run tests, release hygiene, dependency/license review, secret scan, and independent review where available.

## Result vocabulary
Use only `PASS`, `FAIL`, `BLOCKED`, `NOT_RUN`, or `NOT_APPLICABLE`. Never mark a gate PASS if it was not executed.

## Bounded efficiency
Do not run every gate for every task. Select the minimum gate level that covers the actual change, and explain skipped checks when relevant.
