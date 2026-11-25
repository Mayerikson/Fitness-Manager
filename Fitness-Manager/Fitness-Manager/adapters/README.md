# Platform adapters

The portable core is `SKILL.md`. Install the same Skill directory, including its local `fitness_manager/` and `scripts/` runtime, into the host's skill directory. Use `install.ps1` or `install.sh` for the supported filesystem locations documented here. Installers back up an existing target before updating it.

## Claude Code
Personal install: `~/.claude/skills/fitness-manager/`. Project install: `.claude/skills/fitness-manager/`. Claude Code discovers filesystem Skills from these paths.

## Qwen Code
Personal: `~/.qwen/skills/fitness-manager/` or `~/.agents/skills/fitness-manager/`. Project: `.qwen/skills/fitness-manager/` or `.agents/skills/fitness-manager/`. Qwen can also share a skill directory via its `skills.directories` setting.

## Codex
Project skill: `.agents/skills/fitness-manager/`. The host discovers `SKILL.md` and reads references/scripts as needed.

## Grok Build
Project skill: `.grok/skills/fitness-manager/`. Install with `install.ps1 -Grok` or `install.sh --grok`. Verify discovery with `grok inspect` or `/skills`.

## DeepSeek
DeepSeek is a model/provider family, not a universal local Skill host. Use a local or desktop agent runtime that can read filesystem instructions and run Python. If using DeepSeek through an API, that may incur provider charges; the local-first route requires a locally running model and compatible runtime. No DeepSeek API endpoint is configured by this package.

## ChatGPT
Use the package as source material or upload the skill bundle where custom Skill support is available. A standard chat does not automatically have access to the user's local SQLite file. Use workbook/CSV import-export or a supported local execution environment.

## Model-local execution
A local inference runtime (for example Ollama) may run a supported model without per-token provider billing. This does not itself provide skill discovery or agent orchestration: pair it with an agent host that can read files, call local scripts, and preserve user approval. Hardware requirements depend on model size and quantization.
