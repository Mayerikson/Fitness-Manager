# Security Review — Fitness Manager 4.2

## Escopo
Revisão documental e testes locais de pacote. Não é pentest nem certificação.

## Controles adicionados
- Gates explícitos de autorização, evidência, risco, teste e reversão.
- Higiene de evidências e minimização de dados pessoais.
- Tratamento de arquivos/importações como dados não confiáveis.
- Auditoria de release para perfil, SQLite, backups, segredos e chaves.
- QA defensivo limitado ao próprio projeto ou ambiente autorizado.

## Riscos residuais
- Regex de segredos pode gerar falso positivo ou não detectar todos os formatos.
- Auditoria local não substitui revisão humana, SAST, análise de dependências ou pentest autorizado.
- Dados do SQLite ativo continuam protegidos principalmente por permissões do sistema e criptografia integral do disco.
- Agentes podem não respeitar workflows se o host não carregar os arquivos; testar cada adaptador no ambiente real.

## Evidências executadas em 2026-11-24
- `python -m unittest discover -s tests -v`: PASS, 11 testes.
- `python scripts/audit_release.py`: PASS, 125 arquivos inspecionados.
- MYK package audit was run in the original private development workspace; it is not part of this public distribution.

## Não executado
- SAST/DAST externo: NOT_RUN.
- Scanner de dependências: NOT_RUN.
- Pentest: NOT_RUN e fora do escopo desta entrega.
- Teste de instalação real em Claude Code, Qwen Code, Codex e Grok: NOT_RUN.

## Status
Os testes locais e auditorias declarados acima passaram. Isso não constitui certificação de segurança nem validação em cada host de IA. Riscos residuais permanecem conforme listados.
