# UX MVP — três telas principais e uma tela de conclusão

## Princípio

Não construir dezenas de telas antes de validar a jornada principal. O primeiro PWA deve responder a três perguntas do usuário com três superfícies integradas.

## 1. Tela Hoje — O que faço hoje?

Objetivo: reduzir o tempo entre abrir o aplicativo e saber a próxima ação.

Conteúdo:
- Treino programado para hoje e estado (não iniciado, em andamento, concluído).
- Próximo exercício e duração estimada quando conhecida.
- Refeições planejadas e registro rápido.
- Corrida/caminhada prevista, se houver.
- Pendências de check-in (peso, cintura, sono ou recuperação) sem obrigar o usuário a preencher tudo.
- Ações rápidas: registrar texto, gravar áudio, iniciar treino.

## 2. Modo Academia — Como executo e registro?

Objetivo: permitir uso com uma mão, pouca leitura e mínimo de interação.

Conteúdo:
- Exercício atual, séries, repetições e carga anterior.
- Vídeo demonstrativo com origem e estado de verificação.
- Botão de iniciar série, descanso e concluir exercício.
- Registrar carga e repetições sem abrir conversa com LLM.
- Alternativas para aparelho ocupado, classificadas por equivalência documentada; diferenças biomecânicas devem ser visíveis.
- Entrada por texto ou áudio. O sistema mostra a transcrição e os campos interpretados; nada é salvo antes da confirmação explícita.
- Se a alternativa não for suficientemente equivalente ou houver limitação/dor, não sugerir troca automática.

## 3. Dashboard — Estou evoluindo?

Objetivo: mostrar tendências úteis, sem excesso de métricas.

Indicadores iniciais:
- Peso: tendência por semana/mês, sem superinterpretar oscilações diárias.
- Cintura: medidas datadas e comparáveis.
- Treinamento: frequência, cargas e repetições por exercício.
- Corrida: distância, duração e pace, respeitando o objetivo pessoal de até 15 km.
- Adesão: sessões planejadas versus concluídas, sem culpabilização.
- Nutrição: registros e estimativas com origem e incerteza visíveis.


## 4. Tela de conclusão do treino — O que eu realizei?

Objetivo: fechar a sessão com um resumo fiel dos dados efetivamente registrados e oferecer uma transição clara para o histórico. Esta tela é apresentada ao finalizar uma sessão; não precisa ocupar um item permanente da navegação principal.

Conteúdo: 
- Nome do treino e data/hora.
- Duração total calculada a partir dos horários registrados, quando disponíveis.
- Exercícios planejados, concluídos, parcialmente concluídos e ignorados, apresentados separadamente.
- Séries, repetições e cargas efetivamente registradas.
- Substituições realizadas, com exercício original e alternativa escolhida.
- Comparação com a sessão anterior do mesmo programa, somente quando houver dados comparáveis.
- Observação opcional de esforço percebido e comentário do usuário.
- Ações: salvar/confirmar sessão, corrigir registro, ver histórico e compartilhar resumo.

Regras de precisão e privacidade:
- Percentual de conclusão deve ser calculado a partir dos exercícios ou séries definidos no plano, com denominador explícito.
- Não inventar duração, carga, recorde ou exercício concluído quando não houver registro.
- Não exibir estimativa de gasto calórico como medição.
- Compartilhamento é opcional e deve ocultar peso, medidas e outros dados sensíveis por padrão.
- A tela deve permitir corrigir um registro antes de fechar a sessão.
- Sessão parcialmente concluída não deve ser apresentada como 100% concluída.

## Regras transversais

- Mobile-first, acessível e com contraste adequado.
- Funcionalidade básica offline; sincronização futura deve ser explícita e resolver conflitos.
- Não exigir LLM para registros, cálculos ou consulta de histórico.
- Mostrar estados claros: rascunho, aguardando confirmação, salvo, falhou, não reconhecido.
- Não confundir dado ausente com zero.
- Exibir fonte, unidade, data e grau de certeza dos dados relevantes.
- Evitar notificações punitivas, gamificação compulsiva e publicidade invasiva.

## Navegação principal

A navegação principal mantém três áreas: Hoje, Academia e Evolução. A tela de conclusão é um estado contextual após finalizar um treino, acessível também pelo histórico.

## Escopo não incluído no primeiro protótipo

- Feed social, ranking público, chat comunitário, loja, monetização, dezenas de gráficos, prescrições médicas e recomendações automáticas sem aprovação.

## Critérios de aceitação do protótipo

1. Usuário encontra o treino de hoje em uma ação.
2. Usuário abre a instrução/vídeo do exercício sem navegar por menus profundos.
3. Usuário registra série e carga sem LLM.
4. Usuário escolhe uma alternativa com diferenças explicadas quando equipamento está ocupado.
5. Usuário registra por texto/voz, revisa e confirma antes de salvar.
6. Dashboard mostra dados históricos reais e sinaliza estimativas.
7. Ações essenciais continuam disponíveis sem conexão, usando dados já armazenados localmente.
8. Ao finalizar uma sessão, o resumo diferencia itens concluídos, parciais e não realizados, sem inventar métricas.
