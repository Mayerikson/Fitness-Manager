# Fitness Manager 5.1.0-beta.2

## Reliability fixes

- Reject invalid zero values for weight, waist, sets, repetitions, and food quantities before creating a pending record.
- Catch SQLite integrity errors during Telegram confirmation and mark the invalid event as `error`; do not write a health record.
- Process Telegram updates independently and persist the next offset in a per-update `finally` block. A single poison message no longer blocks later messages.
- Use the current local date when `measure --date` is omitted.
- Add regression coverage for all reported failures.
- Align README, Skill metadata, Python package version, and `VERSION`.
- Make the release audit report Python cache directories and adjust CI to clean transient caches before auditing.

## Scope clarification

The PWA, multi-user authentication, automatic biomechanical substitution engine, and WhatsApp gateway are not implemented in this release. Agent Markdown files are role instructions, not autonomous running processes.

## Validation

48 unit/regression tests pass in the local Python 3.13 environment. This does not establish that the GitHub Actions workflow has run remotely or that every supported host has been integration-tested.
