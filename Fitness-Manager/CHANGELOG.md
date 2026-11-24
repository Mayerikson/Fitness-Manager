# Changelog

## 4.3.0 - public handoff preparation
- Prepared a public-safe distribution that excludes private health records and third-party course files.
- Kept the internal MODULE.md convention and the root SKILL.md entry point.
- Added product, architecture, security, and handoff documentation.
- Added CI checks for unit tests and release hygiene.
- Added a blank tracker template; all personal measurements are excluded.
- Replaced bundled MYK source copies with an integration bridge to the author's separate repository.

## 4.2.0
- Added quality gates and evidence hygiene governance modules.
- Added communication-quality workflow inspired by Humanizer's factual-preservation and clarity process; no third-party skill was copied.
- Added defensive-validation workflow inspired by Claude-BugHunter's scope, triage, evidence and QA practices; offensive tooling and payloads were excluded.
- Added quality specialist and third-party provenance register.
- Added Fitness Manager 4.2 SDD artifacts and release-hygiene audit.
- No paid APIs or always-on agents are required.

## 4.1.0
- Integrated a Spec-Driven Development governance bridge while preserving the author's MODULE.md convention.
- Moved personal profile data outside the distributable package.
- Added optional authenticated AES-256-GCM encrypted Google Drive backups.
- Improved restore staging and installer safety.
- Added exercise substitution, training contingency, and food flexibility workflows.

## 3.0.0
- Reorganized into a portable Agent Skills core with platform adapters.
- Added specialist role prompts and dynamic workflows.
- Added local SQLite tracker CLI using Python standard library only.
- Added model-independent local history and backup support.
