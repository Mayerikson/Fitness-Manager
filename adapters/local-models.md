# Local model setup (optional)

A local model runtime can reduce dependence on paid APIs, but it requires compatible hardware and an agent host. A model runtime alone is not a multi-agent orchestrator and does not automatically load Agent Skills.

Suggested architecture:
- Local model runtime: serves inference on the user's computer.
- Agent host: loads `SKILL.md`, routes workflows, and calls local scripts.
- Fitness Manager data layer: SQLite database in `data/`.

Start with a small instruct model that your machine can run reliably. Check RAM/VRAM and model quantization requirements before downloading. Do not assume a large reasoning model will run acceptably on every computer. Keep all records local and do not expose the local service to the public internet.
