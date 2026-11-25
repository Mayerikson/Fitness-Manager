## 5.0.0-beta.3 - Data Integration Engine (Telegram-first)
- Added deterministic Telegram long-polling gateway with numeric sender allowlist and private-chat restriction.
- Added pending confirmation, cancellation, duplicate protection, persistent update offsets, and SQLite ingestion audit.
- Added explicit parsers for weight, waist, running up to 15 km, workout entries, and food quantities.
- Food calories and macronutrients remain unknown unless explicitly supplied; the parser does not invent nutrition values.
- Added optional loopback-only OpenAI-compatible local LLM adapter for explicit `/perguntar` requests; no cloud fallback.
- Added integration documentation and ingestion tests.
- WhatsApp/WAHA remains a future adapter and is not included in this release.

# Changelog

## 5.0.0-beta.1 - stabilization and product foundation
- Added modular `fitness_manager/` Python package and stable CLI wrapper.
- Implemented local SQLite profile, measurements, food logs, workouts, runs, check-ins, plan decisions, and audit events.
- Added append-only historical event tables and a private local profile command.
- Added tested local backup, checksum manifests, integrity verification, restore staging, and pre-restore safety copies.
- Added optional Scrypt-derived AES-256-GCM encryption for Google Drive desktop-sync copies.
- Added 13 unit tests and GitHub Actions CI for Python 3.10–3.13.
- Added safe installers for Claude Code, Codex, Qwen Code, and Grok Build targets; installers copy the Python runtime with the Skill.
- Added proportional quality-gate and evidence-hygiene modules.
- Documented optional UI/UX Pro Max development integration without vendoring it or making it a runtime dependency.
- Added a PWA design brief and optional UI/UX specialist workflow focused on fast gym-mode tasks, accessibility, offline use, and privacy.
- Corrected documentation to distinguish role prompts from executable agents and implemented features from roadmap items.

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
