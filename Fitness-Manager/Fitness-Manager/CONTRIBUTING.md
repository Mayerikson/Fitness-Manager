# Contributing

This repository is currently a personal beta and has no open-source license. Do not assume contributions or reuse are authorized until the owner adds explicit licensing terms.

## Engineering principles

1. Read `SKILL.md`, the relevant workflow, and `governance/MODULE.md` before changing behavior.
2. Preserve `MODULE.md` for internal modules. The root `SKILL.md` remains the portable entry point.
3. Use the MYK SPEC process proportionally for product changes: Discovery, PRD, TechSpec, tasks, implementation, QA, independent review, release.
4. Keep personal records, course files, backups, and credentials out of the repository.
5. Add tests for behavior changes. Use synthetic test data only.
6. Do not add paid APIs, telemetry, or external services without explicit product approval.
7. Document data migrations, backup compatibility, and rollback behavior.
8. Distinguish source-derived facts, external evidence, estimates, and model inference.

## Local validation

```bash
python -m unittest discover -s tests -v
python scripts/audit_release.py .
```

## Pull request expectations

A proposed change should include scope, motivation, affected data, risk, tests, rollback plan, and documentation updates. Changes to health data, encryption, backup, restore, permissions, or synchronization require an explicit threat review.
