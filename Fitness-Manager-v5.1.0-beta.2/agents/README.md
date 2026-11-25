# Specialist role prompts

Files in this directory are **role instructions for an orchestrating agent**. They are not independent executable agents or persistent background processes.

A compatible host may instantiate subagents using these prompts. Other hosts can load the relevant Markdown file into the primary agent. The local Python package performs deterministic data operations; it does not itself create or run LLM agents. `uiux-agent.md` is optional and should be invoked only for interface/design tasks.
