# TechSpec — Fitness Manager 4.2

## Arquitetura
Manter núcleo portátil Agent Skills, `SKILL.md` raiz, workflows sob demanda, agentes especializados e SQLite local. MYK is maintained separately; see `governance/MODULE.md`.

## Convenção de arquivos
- `SKILL.md`: ponto de entrada de Skill que o host reconhece.
- `MODULE.md`: módulo interno de governança/execução mantido conforme convenção do autor e carregado explicitamente pelo ponto de entrada ou adaptador.
- Não renomear automaticamente entre os dois formatos. Claude Code descobre Skills pelo formato/caminho de Skill; um `MODULE.md` não é anunciado como Skill autodescoberta, mas pode ser lido como referência por instrução explícita.

## Novos componentes
- `governance/quality-gates/MODULE.md`
- `governance/evidence-hygiene/MODULE.md`
- `workflows/communication-quality.md`
- `workflows/defensive-validation.md`
- `agents/quality-agent.md`
- `references/THIRD_PARTY_INSPIRATION.md`
- `scripts/audit_release.py`

## Segurança
A auditoria de release verifica ausência de perfil pessoal, banco, backups, arquivos de segredo e padrões comuns de credenciais. O script é um gate auxiliar, não um scanner completo nem prova de ausência de vulnerabilidades.

## Portabilidade e custo
Nenhuma dependência runtime nova. O auditor usa apenas a biblioteca padrão do Python. Nenhum agente adicional é iniciado por padrão; quality-agent e workflows são acionados sob demanda.
