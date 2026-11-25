# Platform compatibility matrix

Verified from public documentation consulted on 2026-11-25. A platform can change support without changing the portable core.

| Host | Filesystem Skill support | Install path / condition |
|---|---|---|
| Claude Code | Yes | `~/.claude/skills/fitness-manager/` or project `.claude/skills/` |
| Qwen Code | Yes | `~/.qwen/skills/`, `~/.agents/skills/`, project `.qwen/skills/` or `.agents/skills/` |
| Codex | Yes | `.agents/skills/fitness-manager/` |
| Grok CLI/build host | Yes, according to xAI Skills docs | `.grok/skills/` or `~/.grok/skills/`; confirm the exact host surface |
| DeepSeek model | Not a standalone Skill runtime | Use an agent host that loads SKILL.md and can execute local scripts |
| ChatGPT | Depends on product surface | Use supported custom Skill upload or provide files/workbook in chat; normal chat does not automatically access local SQLite |

The installer copies the same skill directory to each selected host's documented discovery path. Qwen and Codex use their respective project-level paths in this package; Claude Code and Grok use their host-specific paths. Validate discovery in each installed host.

Sources:
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- https://qwenlm.github.io/qwen-code-docs/en/users/features/skills/
- https://developers.openai.com/blog/skills-agents-sdk
- https://docs.x.ai/build/features/skills-plugins-marketplaces
