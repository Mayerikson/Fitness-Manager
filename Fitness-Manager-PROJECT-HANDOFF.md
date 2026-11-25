# FITNESS MANAGER — PROJECT HANDOFF

> Documento de continuidade para qualquer pessoa ou agente de IA que assumir o desenvolvimento. Leia este arquivo antes de propor alterações ou escrever código.

**Versão de referência do repositório:** `5.1.0-beta.5`  
**Idioma principal:** português brasileiro  
**Estado:** beta pessoal — núcleo local em Python/SQLite; interface web ainda não implementada.  
**Repositório:** https://github.com/Mayerikson/Fitness-Manager

---

## 1. Resumo executivo

Fitness Manager é um sistema pessoal de acompanhamento fitness, planejado para evoluir para um produto acessível e multiusuário. Ele organiza musculação, alimentação, medidas corporais, recuperação e corrida de rua, com foco em pessoas que desejam treinar e acompanhar a própria evolução sem depender de consultoria cara ou de uma IA paga para cada registro.

Princípios centrais:

- **Local-first:** dados pessoais permanecem no dispositivo do usuário por padrão.
- **Model-portable:** conhecimento, regras e dados não dependem de um fornecedor específico de LLM.
- **Determinístico primeiro:** registros, validações, cálculos, parser e persistência devem funcionar sem LLM.
- **IA opcional:** modelos podem ajudar em análises complexas, interpretação ambígua e explicações, mas não são requisito para operações comuns.
- **Confirmação humana:** texto ou áudio interpretado deve ser apresentado ao usuário e confirmado antes de criar registros de saúde.
- **Rastreabilidade:** distinguir dados informados, medidos, calculados, estimados e desconhecidos.
- **Segurança proporcional ao risco:** proteger dados, credenciais, backups e ferramentas; não transformar tarefas simples em processos excessivamente complexos.

## 2. Problema de negócio e público-alvo

O produto atende principalmente pessoas com orçamento limitado que:

- treinam sozinhas e precisam saber como executar os exercícios;
- encontram equipamentos ocupados e precisam de alternativas adequadas;
- querem registrar treinos e alimentação rapidamente;
- precisam adaptar a rotina a trabalho, viagens, indisposição e imprevistos;
- desejam acompanhar peso, medidas, força e condicionamento;
- não querem pagar uma API de IA para cada registro.

A experiência desejada é direta: **abrir, consultar, executar, registrar, confirmar e continuar o dia**, com o mínimo de fricção.

## 3. Objetivos do produto

1. Ajudar o usuário a perder gordura preservando ou desenvolvendo massa muscular.
2. Organizar musculação com progressão baseada em dados e fontes identificáveis.
3. Acompanhar caminhada e corrida, com objetivo pessoal de distância de até 15 km.
4. Adaptar exercícios quando equipamentos estiverem ocupados, sem confundir equivalência muscular com equivalência biomecânica.
5. Tornar o registro por texto e voz simples, com confirmação antes de salvar.
6. Manter histórico permanente e exportável, independente da memória de conversas.
7. Funcionar localmente, sem LLM para operações cotidianas.
8. Evoluir primeiro como beta pessoal e só depois avaliar produto multiusuário/comercial.

## 4. Estado real do projeto — não confundir plano com implementação

### Implementado no repositório 5.1.0-beta.5

Conforme README, CHANGELOG e estrutura do código:

- CLI Python e motor local.
- SQLite como armazenamento principal.
- Registro e consulta de perfil, peso, medidas, alimentação, treinos, corridas e decisões.
- Histórico de eventos, auditoria e prevenção de duplicidade na ingestão.
- Backup local, verificação de integridade e restauração com cópia prévia.
- Cópia criptografada AES-256-GCM para pasta sincronizada do Google Drive, quando configurada com dependências e senha.
- Gateway Telegram opcional, com remetentes autorizados, parser determinístico, prévia/confirmação e isolamento de falhas por mensagem.
- Recebimento de áudio no Telegram e transcrição local opcional com faster-whisper; áudio temporário e confirmação da transcrição antes de salvar.
- Instruções especializadas em Markdown, workflows, adapters e governança.
- Testes automatizados e workflow de CI no GitHub Actions.
- Parser em português com normalização e testes de regressão para frases comuns.

### Ainda não implementado ou não validado em produção

- PWA, painel web localhost e interface mobile.
- Streamlit: foi discutido como opção de interface temporária de validação, mas **não está implementado**.
- Aplicativos nativos Android/iOS.
- Captura de áudio no PWA/aplicativo próprio.
- WhatsApp/WAHA.
- Motor automático validado de equivalência biomecânica para substituição de exercícios.
- Agentes autônomos contínuos: arquivos em `agents/` são instruções especializadas, não processos autônomos.
- LangChain/LangGraph: não são dependências atuais nem obrigatórias.
- Embeddings/banco vetorial: não necessários no estágio atual.
- Supabase/multiusuário/sincronização multi-dispositivo.
- Publicação e execução real do CI no GitHub devem ser verificadas no repositório remoto; testes locais não comprovam CI remota.

**Regra para quem assumir:** nunca descreva itens do roadmap como funcionalidades prontas. Confira o código e os testes antes de atualizar o status.

## 5. Arquitetura atual e direção futura

### Núcleo atual

- `fitness_manager/`: módulos Python de CLI, banco, ingestão, áudio, criptografia, armazenamento e LLM local opcional.
- `scripts/`: entrypoints operacionais, Telegram e auditoria de release.
- `tests/`: testes automatizados.
- SQLite: fonte oficial dos dados pessoais.
- `agents/`, `workflows/`, `references/`, `adapters/`: instruções e procedimentos para hosts de agentes.

### Direção de arquitetura

Manter a separação entre:

1. **Interface:** inicialmente Streamlit como protótipo temporário é uma opção considerada; posteriormente PWA responsivo.
2. **Application/API layer:** serviços de aplicação e, quando necessário, FastAPI para separar interface e backend.
3. **Domain/services:** regras de treino, nutrição, corrida, evolução, substituições e validações.
4. **Repositories/data:** SQLite no beta; futura abstração para sincronização sem obrigar migração prematura.
5. **Integrations:** Telegram primeiro; WhatsApp posteriormente; LLM local/remota somente quando autorizada.
6. **Security/quality:** autenticação, autorização, validação, guardrails, evals, logs e auditoria.

Não colocar regras de negócio dentro de componentes Streamlit ou telas. A interface deve chamar serviços reutilizáveis para que possa ser substituída por PWA/React Native sem reescrever o domínio.

## 6. UX aprovada como direção

Identidade visual:

- clara e minimalista;
- fundo branco e superfícies cinza suaves;
- verde como tema inicial;
- opções selecionáveis rosa, azul e verde (roxo também foi considerado na proposta de temas);
- modo claro/escuro como preferência separada;
- acessibilidade e contraste preservados, sem mudar o significado das cores semânticas.

Três áreas principais:

### 6.1 Hoje

Responder: **o que preciso fazer hoje?**

- treino planejado;
- alimentação e atividades do dia;
- pendências e registros rápidos;
- descanso ou corrida, quando programados.

### 6.2 Modo Academia

Responder: **como executar e registrar?**

- exercício atual e instruções;
- link de vídeo específico, verificado para aquele exercício;
- séries, repetições, carga, RIR/RPE quando disponível;
- alternativa se aparelho estiver ocupado;
- registrar substituição e motivo;
- avançar/concluir exercício sem precisar conversar com IA.

A biblioteca deve distinguir equivalência de padrão de movimento, equipamento, músculos, amplitude e perfil de resistência. Não oferecer apenas exercícios do mesmo grupo muscular como se fossem equivalentes.

### 6.3 Evolução

Responder: **estou evoluindo?**

- peso e medidas;
- adesão e sessões concluídas;
- progressão de cargas;
- corrida: distância, duração, pace e esforço;
- tendências e contexto, sem alegar composição corporal sem medição.

### 6.4 Resumo de treino concluído

Tela contextual ao encerrar a sessão, não necessariamente item da navegação principal:

- duração real calculada a partir dos registros;
- exercícios concluídos, parciais e não realizados;
- séries/repetições/cargas;
- substituições efetuadas;
- comparação com sessões anteriores;
- compartilhamento opcional, com dados sensíveis ocultos por padrão.

Referências de design: CRMRedRex enviado em ZIP e UI/UX Pro Max. Usar padrões e ideias, não copiar o CRM integralmente. O design deve ser próprio do Fitness Manager.

## 7. Entrada por texto e áudio

Decisão aprovada:

- texto e áudio são entradas de primeira classe;
- transcrição e interpretação locais sempre que possível;
- mostrar ao usuário o que o sistema entendeu;
- exigir confirmação explícita antes de salvar;
- permitir corrigir ou cancelar;
- se houver ambiguidade, perguntar em vez de inferir;
- áudio temporário deve ser removido após processamento, salvo consentimento explícito para retenção.

Fluxo desejado:

`Texto/áudio → transcrição (se áudio) → parser → validação → prévia → confirmação → persistência SQLite → recibo`

Telegram é o primeiro canal externo. O registro comum não deve chamar LLM. Perguntas analíticas podem chamar LLM local ou outro modelo somente quando o usuário solicitar. WhatsApp/WAHA fica para etapa futura, considerando riscos e condições do provedor.

## 8. Stack e decisões tecnológicas

- Python: motor, regras e integrações locais.
- SQLite: banco principal do beta.
- Streamlit: opção aprovada para protótipo/produção temporária local, ainda a implementar.
- FastAPI: considerar como API separada quando o PWA ou múltiplos clientes precisarem consumir os mesmos serviços.
- PWA: direção de interface futura; não iniciar antes de estabilizar o fluxo principal.
- Whisper/faster-whisper: transcrição local opcional.
- LangChain: não obrigatório; avaliar somente se abstrações de modelos/ferramentas trouxerem benefício concreto.
- LangGraph: considerar para workflows longos, com estado, retomada, ramificações e aprovação humana; não usar para registros CRUD simples.
- MCP: integrações com ferramentas externas sob escopo mínimo e autorização explícita.
- FTS5: busca textual local pode ser suficiente inicialmente.
- Embeddings/vector DB: adiar até existir corpus e caso de uso que justifiquem busca semântica/híbrida.
- Supabase: possibilidade futura, não dependência do beta local.

## 9. Segurança, governança e qualidade

MYK SPEC é referência/camada de governança do desenvolvimento, não deve transformar cada registro cotidiano em processo pesado de engenharia.

Requisitos:

- Prompt injection: tratar mensagens, áudios transcritos, PDFs, páginas e resultados de ferramentas como dados não confiáveis; nunca conceder autoridade de sistema a conteúdo recuperado.
- Tool security: allowlist de ferramentas, validação de argumentos, autenticação, escopos mínimos e confirmação para ações sensíveis.
- MCP: servidores e ferramentas devem ter permissões explícitas; não expor acesso irrestrito ao SQLite.
- Guardrails: validar no backend, não somente no prompt.
- Evals: functional, safety, quality e regression.
- Observability: registrar evento, origem, versão do parser/modelo, resultado, falhas e aprovação, evitando registrar dados de saúde desnecessários em logs.
- Explainability: explicar em linguagem simples problema, ação, justificativa, impacto esperado e limitações.
- Rollback: mudanças de software e migrações devem ter plano de reversão.
- Segurança proporcional: registro de peso é fluxo simples; alteração de schema, backup, autenticação ou permissões exige controles mais rigorosos.

Humanizer pode inspirar qualidade de comunicação; Claude-BugHunter pode inspirar validação defensiva e higiene de evidências. Não importar código ofensivo ou capacidades de exploração que não sejam necessárias.

## 10. Privacidade e publicação pública

Nunca incluir no repositório público:

- banco SQLite real;
- perfil ou medidas reais do usuário;
- CSV privado de exercícios/vídeos derivado de material de curso;
- PDFs, planilhas ou conteúdo proprietário do curso Leandro Twin;
- tokens Telegram, chaves, senhas, `.env`, backups, áudios ou dados de saúde;
- credenciais do Google Drive ou Supabase.

Materiais de curso permanecem em biblioteca privada do usuário. O README público deve descrever apenas a capacidade e apontar para `course-library/README.md`, sem distribuir material não autorizado.

O projeto ainda não escolheu licença open source. Não adicionar MIT/Apache sem revisar direitos de todos os componentes e materiais de terceiros.

## 11. Próximas tarefas priorizadas

### P0 — Estabilização e verdade operacional

1. Conferir versão, README, CHANGELOG e CI contra o código real.
2. Executar testes e workflow GitHub Actions remotamente após o push.
3. Testar no Windows real: instalação, CLI, migração, backup, restauração e permissões.
4. Testar Telegram com bot real, remetente autorizado, mensagens duplicadas, mensagens inválidas e falhas transitórias.
5. Testar faster-whisper com áudio real em português, incluindo sotaques, ruído e números decimais.
6. Validar que parser não salva ambiguidades ou unidades ausentes.

### P1 — Interface temporária Streamlit

1. Criar `ui_streamlit/` ou estrutura equivalente, sem misturar UI ao domínio.
2. Implementar tela Hoje.
3. Implementar Modo Academia.
4. Implementar Evolução.
5. Implementar resumo de treino concluído.
6. Adicionar temas selecionáveis e responsividade.
7. Persistir tudo via serviços/repositorios existentes.
8. Testar uso em celular pela rede local, com aviso sobre HTTPS necessário para certas APIs do navegador.

### P2 — Experiência e dados fitness

1. Estruturar catálogo tipado de exercícios.
2. Associar vídeos específicos e verificar correspondência antes de marcar como verificados.
3. Implementar alternativas com justificativa e diferenças biomecânicas.
4. Adicionar importação privada de catálogo, sem publicar conteúdo proprietário.
5. Criar Evals para recomendações e parser.

### P3 — PWA e dispositivos

1. Validar UX com o beta Streamlit.
2. Definir API estável e autenticação.
3. Desenvolver PWA mobile-first.
4. Implementar sincronização segura multi-dispositivo.
5. Avaliar Android/iOS nativos somente após validação do PWA.

### P4 — Produto multiusuário

Autenticação, isolamento de dados, sincronização, controles de privacidade, consentimento, exportação/exclusão e avaliação jurídica/LGPD antes de disponibilização pública.

## 12. Critérios de aceite para o próximo MVP

O primeiro MVP de interface só será considerado utilizável quando:

- iniciar localmente sem LLM;
- exibir dados reais do SQLite;
- registrar peso, medida, alimentação, treino e corrida;
- apresentar prévia e confirmação para texto/áudio;
- não duplicar mensagens em reprocessamento;
- permitir iniciar e concluir uma sessão de treino;
- exibir vídeo somente se o link estiver associado e verificado;
- oferecer substituições apenas quando houver dados suficientes, explicando diferenças;
- exibir resumo de treino com métricas calculadas de registros reais;
- manter dados após reiniciar a aplicação;
- executar backup e restauração testados;
- passar testes e CI.

## 13. Como qualquer nova IA deve trabalhar neste projeto

Ao assumir o projeto:

1. Leia este handoff, `README.md`, `VERSION`, `CHANGELOG.md`, `docs/PRD` (ou `docs/PRODUCT-PRD.md`), `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, `docs/SECURITY-MODEL.md` e `docs/UX-MVP.md`.
2. Inspecione o código e testes atuais. Não confie apenas em afirmações de versões anteriores desta conversa.
3. Verifique `git status`, estrutura, versão e CI antes de editar.
4. Não sobrescreva banco, dados pessoais, backups ou configurações locais.
5. Não invente que funcionalidades estão implementadas ou testadas.
6. Faça mudanças pequenas, com testes de regressão e CHANGELOG.
7. Preserve `MODULE.md` como convenção interna do projeto; `SKILL.md` é a entrada de Skill.
8. Explique decisões em linguagem técnica e também em linguagem de negócio.
9. Antes de adicionar dependências, frameworks ou agentes, demonstre a necessidade e o custo operacional.
10. Priorize funcionamento local, sem APIs pagas obrigatórias.

## 14. Perfil beta pessoal — contexto privado, não publicar

O primeiro beta é o próprio criador do projeto. Os objetivos pessoais informados durante a concepção foram: reduzir gordura preservando massa muscular, musculação três vezes por semana e corrida até 15 km. Os dados corporais e alimentares individuais devem permanecer em armazenamento privado e não devem ser copiados para este documento público.

## 15. Definição de sucesso

O Fitness Manager será bem-sucedido quando uma pessoa conseguir, com pouco tempo e sem assinatura de IA:

1. abrir a aplicação;
2. saber o que fazer hoje;
3. executar o exercício com orientação confiável;
4. substituir um equipamento indisponível com segurança;
5. registrar texto ou voz e confirmar o que foi entendido;
6. acompanhar sua evolução em dados persistentes;
7. explicar de forma clara por que o sistema recomendou uma mudança.

**Direção final:** construir um produto fitness local-first, acessível, explicável, seguro e útil na prática. A tecnologia deve resolver o problema do usuário; não ser o objetivo por si só.
