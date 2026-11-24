# DeepSeek setup

DeepSeek is treated as a model choice, not as a universal Skill host. Select a local agent runtime that can:
1. Read this directory and `SKILL.md`.
2. Access the local SQLite database.
3. Execute the standard-library Python script.
4. Respect user approval before changing training/nutrition plans.

If the runtime supports a locally hosted DeepSeek-family model, configure it there. If it uses a hosted DeepSeek API, provider billing or rate limits may apply. No API key, remote endpoint, or provider call is included in this package.
