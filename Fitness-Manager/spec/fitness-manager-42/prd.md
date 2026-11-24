# PRD — Fitness Manager 4.2

## Problema
O produto já possui núcleo local, workflows e governança MYK. A avaliação dos repositórios Humanizer e Claude-BugHunter identificou oportunidades em qualidade de comunicação, higiene de evidências, validação por gates e QA defensivo.

## Objetivos
- Adicionar validação proporcional para decisões e mudanças relevantes.
- Proteger dados pessoais em relatórios, exports e evidências.
- Melhorar clareza sem alterar fatos ou incertezas.
- Formalizar testes defensivos em ambiente próprio/autorizado.
- Registrar proveniência das inspirações de terceiros.
- Preservar `governance/MODULE.md` e a estrutura original do MYK.

## Fora de escopo
- Importar o bundle ofensivo do Claude-BugHunter.
- Importar integralmente o Humanizer.
- Testes em sistemas de terceiros.
- Reescrita automática de mensagens pessoais.
- Novas APIs pagas, serviços hospedados ou agentes sempre ativos.

## Critérios de aceitação
- CA-01: os módulos `MODULE.md` existem e não são renomeados para `SKILL.md`.
- CA-02: o `SKILL.md` raiz permanece o ponto de entrada portátil do Fitness Manager.
- CA-03: todo resultado de QA distingue PASS, FAIL, BLOCKED, NOT_RUN e NOT_APPLICABLE.
- CA-04: relatórios preservam fatos, números, fontes e incertezas.
- CA-05: exportações e evidências seguem minimização e revisão de dados pessoais.
- CA-06: testes defensivos limitam-se ao projeto e ambientes autorizados.
- CA-07: auditoria de release rejeita perfil pessoal, banco, backups e segredos no pacote.
- CA-08: proveniência e limites das referências Humanizer/BugHunter são documentados.
