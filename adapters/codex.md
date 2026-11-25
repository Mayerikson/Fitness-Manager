# Codex setup

Codex supports repo-local Agent Skills in `.agents/skills/`.

1. Run `install.ps1 -Codex -ProjectPath <project>` on Windows or `bash install.sh --codex --project <project>` on macOS/Linux.
2. Open the project in Codex.
3. Ask Codex to list available Skills, then invoke `$fitness-manager` or request a workflow in natural language.
4. Keep `data/fitness_manager.sqlite` in a local private directory; do not commit personal body/health records to a public repository.
