# Developer handoff

## Current state

Fitness Manager is a single-user, local-first beta candidate. The repository contains the portable Skill, workflows, role prompts, SQLite CLI, blank tracker, tests, adapters, governance bridge, and product specifications.

## Important conventions

- Keep the root entry point named `SKILL.md`.
- Preserve the author's internal `MODULE.md` naming. Claude Code does not auto-discover arbitrary `MODULE.md` files; the root Skill or adapter must load them explicitly.
- The MYK SPEC project remains separate at https://github.com/Mayerikson/Spec. This repository contains only `governance/MODULE.md`, not a copy of the MYK package.
- Do not bundle course PDFs, spreadsheets, exercise tables, or extracted course text. The private course library belongs outside the public repository.

## First-run checklist

1. Install Python 3.9+.
2. Run `python scripts/fitness_manager.py init`.
3. Run `python scripts/fitness_manager.py report`.
4. Install the Skill in one host using the matching adapter.
5. Run the unit tests and release audit.
6. Create a local backup and test restoration using synthetic data before entering real personal data.
7. Configure encrypted Google Drive backup only after setting a strong local passphrase and verifying the desktop sync directory.

## Known limitations

- No real-host integration tests have been completed for every provider.
- DeepSeek is a model provider, not a guaranteed filesystem Skill runtime.
- Native subagent behavior varies by host.
- The exercise/course library is intentionally not included in the public distribution.
- The release audit is not a full security scanner.
- No public license has been selected.

## Release gates

- Unit tests pass.
- `scripts/audit_release.py` passes.
- No personal data, secrets, private course material, database, or backup is present.
- Backup and restore have been tested with synthetic data.
- README and changelog match the actual package.
- Any third-party files have compatible licenses and required notices.
