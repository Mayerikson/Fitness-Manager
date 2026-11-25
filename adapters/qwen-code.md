# Qwen Code setup

Qwen Code supports personal Skills under `~/.qwen/skills/` and `~/.agents/skills/`, and project Skills under `.qwen/skills/` and `.agents/skills/`. This package installs to the shared `.agents/skills/` location so the same copy can also be discovered by Codex.

1. Run `install.ps1 -QwenCode` on Windows or `bash install.sh --qwen` on macOS/Linux.
2. In Qwen Code, inspect `/skills` and invoke `/fitness-manager` or ask naturally.
3. If needed, configure `skills.directories` to point to the folder you manage.
