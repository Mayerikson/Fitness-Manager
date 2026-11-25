# Claude Code setup

1. Run `powershell -ExecutionPolicy Bypass -File .\\install.ps1 -ClaudeCode` on Windows, or `bash install.sh --claude` on macOS/Linux.
2. Restart/reload Claude Code if needed.
3. Ask: `Use the fitness-manager skill. Show my current baseline and available workflows.`
4. To use the local tracker, allow the agent to run `python scripts/fitness_manager.py ...` in the extracted project folder.


## Naming compatibility
Preserve any project-authored `MODULE.md` files and invoke them using the path/convention defined by that project. Do not rename them to `SKILL.md`. The Fitness Manager root `SKILL.md` is a separate portable entrypoint; it does not replace or rename MYK modules. Validate discovery in the actual Claude Code environment before claiming installation success.
