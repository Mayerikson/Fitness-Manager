# MODULE — Quality Gates e Validação de Decisões

## Finalidade
Adaptar ao Fitness Manager as práticas de validação por etapas, triagem, escopo e evidência observadas no Claude-BugHunter, sem importar técnicas ofensivas ou conteúdo de exploração.

## Gate para ações relevantes
Antes de recomendar ou executar uma mudança relevante, responder de forma verificável:
1. **Objetivo:** qual problema concreto a mudança resolve?
2. **Escopo e autorização:** o pedido do usuário autoriza esta ação? O agente tem permissão técnica para executá-la?
3. **Evidência:** quais registros, fontes ou medições sustentam a decisão? Qual a data e a qualidade desses dados?
4. **Risco:** há risco físico, clínico, de privacidade, perda de dados, custo ou indisponibilidade?
5. **Alternativas:** existe opção menos arriscada e reversível?
6. **Validação:** quais testes ou critérios demonstrarão que a mudança funcionou?
7. **Reversão e acompanhamento:** como desfazer a mudança e quando medir o resultado?

## Estados permitidos
- `PASS`: evidência e testes exigidos foram efetivamente verificados.
- `FAIL`: uma condição obrigatória falhou.
- `BLOCKED`: falta autorização, dado essencial ou condição de segurança.
- `NOT_RUN`: a verificação não foi executada.
- `NOT_APPLICABLE`: a verificação não se aplica, com justificativa.

Nunca converter `NOT_RUN`, `BLOCKED` ou ausência de evidência em `PASS`.

## Aplicação por risco
- Registro rotineiro informado pelo usuário: validação de formato e origem; não executar cerimônia completa.
- Alteração de treino ou alimentação: apresentar proposta, evidência, limites e obter aprovação do usuário antes de substituir o plano vigente.
- Alteração de banco, criptografia, backup, sincronização, autenticação ou exportação: exigir PRD/TechSpec proporcional, análise de ameaças, testes de regressão e plano de restauração.
- Distribuição para terceiros: executar auditoria de pacote, revisão de segredos, privacidade, licenças e documentação.

## Escopo de segurança
Testes são limitados ao próprio Fitness Manager, ao ambiente local do usuário ou a ambientes de teste expressamente autorizados. Não incluir varredura externa, exploração de terceiros, persistência, evasão, malware ou coleta de credenciais.

## Critério de conclusão
Toda mudança relevante gera um registro com requisito, risco, evidência, testes executados, resultado, limitações, aprovação e plano de reversão.
