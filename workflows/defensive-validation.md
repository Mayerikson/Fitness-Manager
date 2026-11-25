# Workflow — Validação Defensiva do Produto

## Objetivo
Aplicar validação estruturada e testes defensivos somente ao código, dados e ambientes autorizados do Fitness Manager.

## Escopo permitido
- Validação local de entradas e saídas.
- Testes de autorização e isolamento de dados do próprio aplicativo.
- Verificação de arquivos distribuíveis e segredos acidentalmente incluídos.
- Testes de backup, restauração, integridade e migração.
- Testes de prompt injection com fixtures inofensivas e dados sintéticos.
- Revisão de dependências, permissões e comportamento de instaladores.

## Procedimento
1. Confirmar o repositório, versão, branch e ambiente de teste.
2. Confirmar que o alvo é o próprio projeto ou ambiente autorizado.
3. Ler requisitos, TechSpec, política de segurança e estado atual do repositório.
4. Criar casos de teste com dados sintéticos; nunca usar dados pessoais reais sem necessidade.
5. Verificar entradas malformadas, limites, duplicidade, falhas parciais e recuperação.
6. Verificar que conteúdo importado não pode instruir o agente a ignorar políticas ou acessar arquivos fora do escopo.
7. Executar testes automatizados e registrar os comandos e resultados reais.
8. Revisar diffs e artefatos de distribuição em busca de perfil, banco, backup, segredo ou dado pessoal.
9. Registrar limitações. Scanner indisponível significa `NOT_RUN`, não `PASS`.

## Proibições
Não executar exploração de sistemas de terceiros, enumeração externa, brute force, evasão, persistência, exfiltração, malware ou coleta de credenciais. O projeto não precisa importar o catálogo ofensivo do Claude-BugHunter.
