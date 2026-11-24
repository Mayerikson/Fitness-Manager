# Fitness Manager

### Inteligência pessoal para treinamento, nutrição e evolução física.

O **Fitness Manager** é um projeto de acompanhamento físico baseado em inteligência artificial, arquitetura local-first e workflows adaptativos.

Seu objetivo é tornar o treinamento, a alimentação e o acompanhamento da evolução mais acessíveis, organizados e independentes de plataformas específicas de IA.

A proposta é simples: ajudar pessoas a cuidar da própria saúde, mesmo com orçamento limitado, sem depender de consultorias caras ou interações constantes com um assistente.

> **Treinar. Adaptar. Registrar. Evoluir.**

---

## Status do projeto

**Versão:** 4.3.0 — Public Handoff  
**Estágio:** Beta pessoal  
**Arquitetura:** Local-first e model-portable  
**Banco principal:** SQLite  
**Interface futura:** Progressive Web App (PWA)

O projeto está em desenvolvimento e ainda não representa um produto comercial ou clinicamente validado.

## 1. Visão do produto

O Fitness Manager nasceu como um sistema pessoal de acompanhamento físico, mas sua arquitetura foi planejada para permitir uma futura aplicação multiusuário.

O produto pretende atender principalmente pessoas que:

- Possuem orçamento limitado.
- Treinam sem acompanhamento individual.
- Precisam aprender a execução dos exercícios.
- Encontram aparelhos ocupados na academia.
- Precisam adaptar seus treinos à rotina.
- Querem organizar a alimentação sem dietas complexas.
- Desejam acompanhar resultados com dados históricos.
- Não querem depender de um único fornecedor de inteligência artificial.

A experiência deve ser objetiva: consultar o planejamento, executar a atividade, registrar o resultado e continuar a rotina.

## 2. Principais funcionalidades

### Treinamento adaptativo

- Organização de diferentes divisões de treinamento.
- Biblioteca de metodologias e exercícios.
- Registro de séries, repetições e cargas.
- Acompanhamento de desempenho.
- Avaliação de recuperação.
- Recomendações de progressão.
- Histórico de alterações.

O material de treinamento do Leandro Twin é utilizado como referência para os programas disponibilizados pelo usuário, respeitando a distinção entre conteúdo original e adaptações técnicas.

### Substituição inteligente de exercícios

Quando um equipamento estiver ocupado ou indisponível, o sistema poderá apresentar alternativas considerando:

- Grupo muscular.
- Padrão de movimento.
- Biomecânica.
- Equipamento disponível.
- Experiência do usuário.
- Limitações físicas.

As substituições devem apresentar diferenças relevantes, não apenas nomes de exercícios que trabalham músculos semelhantes.

### Plano de contingência

O sistema deve adaptar a programação diante de:

- Falta de tempo.
- Academia cheia.
- Indisponibilidade de equipamentos.
- Indisposição leve.
- Interrupções na rotina.
- Doenças ou lesões que exijam suspensão do treinamento.

A recuperação e a segurança têm prioridade sobre a manutenção artificial de uma sequência de treinos.

### Nutrição adaptativa

- Registro de refeições.
- Estimativa de calorias e macronutrientes.
- Planejamento alimentar semanal.
- Adaptação ao orçamento.
- Substituição de alimentos.
- Organização de refeições antecipadas.
- Flexibilidade para viagens e datas comemorativas.

### Corrida e condicionamento cardiovascular

O módulo cardiovascular permite acompanhar:

- Caminhadas.
- Corridas.
- Distância percorrida.
- Tempo de atividade.
- Pace.
- Percepção de esforço.
- Evolução da resistência.

O planejamento pessoal inicial contempla corridas de até 15 km.

### Monitoramento corporal

- Peso.
- Circunferência abdominal.
- Medidas corporais.
- Histórico de composição corporal, quando disponível.
- Fotografias de evolução, quando fornecidas.
- Comparativos semanais e mensais.

Os indicadores devem ser interpretados como tendências, sem confundir oscilações de peso com alterações comprovadas de gordura ou massa muscular.

## 3. Arquitetura

O projeto separa conhecimento, inteligência, dados e execução.

```text
Fitness-Manager/
│
├── SKILL.md
│
├── agents/
│   ├── training-agent.md
│   ├── nutrition-agent.md
│   ├── progress-agent.md
│   ├── running-agent.md
│   ├── evidence-agent.md
│   └── quality-agent.md
│
├── workflows/
│   ├── training-review.md
│   ├── nutrition-review.md
│   ├── exercise-substitution.md
│   ├── training-contingency.md
│   ├── program-change.md
│   └── ...
│
├── governance/
│   └── MODULE.md
│
├── references/
│
├── scripts/
│   └── fitness_manager.py
│
├── tests/
│
├── adapters/
│
├── docs/
│
├── spec/
│
├── templates/
│
└── data/
```

### SKILL.md versus MODULE.md

O projeto utiliza intencionalmente dois formatos:

- `SKILL.md`: ponto de entrada reconhecido pelos ambientes compatíveis com Agent Skills.
- `MODULE.md`: módulos internos de governança, contratos e procedimentos especializados.

A nomenclatura `MODULE.md` é preservada por decisão arquitetural do projeto e não deve ser substituída indiscriminadamente por `SKILL.md`.

### Agentes especializados

Os agentes são módulos de responsabilidade específica.

A arquitetura prevê:

- Training Agent.
- Nutrition Agent.
- Progress Agent.
- Running Agent.
- Evidence Agent.
- Quality Agent.

Eles não precisam ser executados simultaneamente. O orquestrador seleciona o workflow necessário para cada solicitação.

## 4. Governança e segurança

O Fitness Manager incorpora conceitos do projeto MYK SPEC, mantido separadamente por seu autor.

A governança contempla:

- Especificações rastreáveis.
- Revisão de requisitos.
- Validação de alterações.
- Quality Gates.
- Segurança defensiva.
- Auditoria.
- Explainability.
- Observability.
- Bounded Efficiency.

Também utiliza referências metodológicas dos projetos Humanizer e Claude-BugHunter.

Esses projetos são referências de inspiração metodológica. Seus códigos não estão incorporados automaticamente ao Fitness Manager.

### Princípio de rastreabilidade

Toda alteração relevante deve identificar:

1. Dados utilizados.
2. Origem das informações.
3. Problema identificado.
4. Decisão tomada.
5. Justificativa.
6. Resultado esperado.
7. Critério de reavaliação.

Nenhuma alteração de treinamento ou alimentação deve ocorrer silenciosamente.

## 5. Armazenamento e persistência

O projeto adota uma arquitetura local-first.

O SQLite é a fonte principal dos registros pessoais.

O histórico pode contemplar:

- Perfil.
- Medidas.
- Alimentação.
- Treinamentos.
- Corridas.
- Check-ins.
- Programas.
- Decisões.
- Auditoria.

### Localização dos dados

Windows:

```text
%USERPROFILE%\.fitness-manager\
```

macOS/Linux:

```text
~/.fitness-manager/
```

O banco de dados não deve ser armazenado dentro do repositório público.

### Backups

O sistema contempla:

- Backups locais.
- Manifestos SHA-256.
- Verificação de integridade.
- Restauração controlada.
- Cópia de segurança antes da restauração.
- Retenção configurável.

A sincronização com Google Drive utiliza uma pasta privada e deve empregar criptografia antes do envio dos arquivos.

SHA-256 permite detectar alterações nos arquivos, mas não substitui uma assinatura digital nem protege contra um atacante com privilégios locais.

A integração com Supabase permanece como possibilidade futura, não como dependência obrigatória.

## 6. Independência de modelos

O conhecimento e os dados devem permanecer independentes do fornecedor de IA.

O projeto possui orientações de adaptação para:

- Claude Code.
- OpenAI Codex.
- Qwen Code.
- Ambientes compatíveis com Grok.
- Agentes que utilizam modelos DeepSeek.
- Modelos locais através de runtimes compatíveis.

A compatibilidade depende do ambiente de execução, não apenas do modelo.

Um modelo de IA isolado não garante descoberta de Skills, acesso ao SQLite ou execução dos workflows.

O projeto prioriza execução local e não exige uma API paga para registros, cálculos e operações locais.

## 7. Instalação

### Requisitos

- Python 3.9 ou superior.
- Sistema operacional compatível.
- Ambiente agente capaz de carregar arquivos e executar scripts.
- Dependência adicional para backups criptografados, quando utilizada.

### Windows

Inicializar o banco:

```powershell
python .\scripts\fitness_manager.py init
```

Consultar o histórico:

```powershell
python .\scripts\fitness_manager.py report
```

Instalar no Claude Code:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -ClaudeCode
```

### macOS/Linux

Inicializar:

```bash
python3 scripts/fitness_manager.py init
```

Consultar histórico:

```bash
python3 scripts/fitness_manager.py report
```

Instalar no Codex:

```bash
bash install.sh --codex
```

Consulte `adapters/` para orientações específicas de cada ambiente.

## 8. Operações do banco de dados

Consultar histórico:

```bash
python scripts/fitness_manager.py history --limit 50
```

Registrar pesagem:

```bash
python scripts/fitness_manager.py weigh-in \
  --weight 73.4 \
  --date 2025-01-10
```

Registrar medida:

```bash
python scripts/fitness_manager.py measure \
  --kind waist \
  --value 84 \
  --unit cm \
  --date 2025-01-10 \
  --method "horizontal at navel"
```

Registrar treinamento:

```bash
python scripts/fitness_manager.py workout \
  --date 2025-01-10 \
  --session A \
  --exercise "Example exercise" \
  --sets 2 \
  --reps 12 \
  --load-kg 10 \
  --rir 3
```

Registrar corrida:

```bash
python scripts/fitness_manager.py run \
  --date 2025-01-11 \
  --distance-km 3 \
  --duration-min 24 \
  --rpe 4
```

Os valores apresentados são exemplos sintéticos para demonstrar os comandos, não prescrições de treinamento.

## 9. Desenvolvimento e testes

Executar os testes:

```bash
python -m unittest discover -s tests -v
```

Executar auditoria de distribuição:

```bash
python scripts/audit_release.py .
```

O projeto utiliza GitHub Actions para verificações automatizadas.

A auditoria de distribuição não substitui SAST, análise completa de dependências, pentest ou certificação independente de segurança.

## 10. Roadmap

### Fase 1 — Beta pessoal

- Skill universal.
- Agentes especializados.
- Banco SQLite.
- Histórico permanente.
- Backups.
- Biblioteca de treinamento.
- Alimentação e corrida.

### Fase 2 — Experiência mobile

- PWA.
- Modo academia.
- Substituição de exercícios.
- Biblioteca de execução.
- Recursos offline.

### Fase 3 — Inteligência de dados

- Indicadores de adesão.
- Análise de desempenho.
- Melhoria contínua.
- Relatórios de evolução.
- Detecção de dificuldades recorrentes.

### Fase 4 — Multiusuário

- Perfis independentes.
- Autenticação.
- Isolamento de dados.
- Sincronização em nuvem.
- Controles de privacidade.

### Fase 5 — Produto comercial

- Avaliação de modelo gratuito.
- Recursos premium opcionais.
- Monetização acessível.
- Possível distribuição em lojas de aplicativos.

As fases futuras representam planejamento, não funcionalidades já entregues.

## 11. Privacidade e responsabilidade

O Fitness Manager trabalha com informações que podem ser consideradas dados pessoais sensíveis, especialmente registros relacionados à saúde.

Por isso:

- Não publique bancos de dados pessoais.
- Não publique backups.
- Não inclua credenciais ou tokens.
- Não compartilhe perfis individuais.
- Não inclua materiais proprietários de terceiros sem autorização.
- Preserve o consentimento e o isolamento de dados em futuras versões multiusuário.

O Fitness Manager não é um dispositivo médico e não substitui avaliação médica, nutricional ou acompanhamento de profissional de educação física.

## 12. Materiais de terceiros

Os materiais do curso Leandro Twin utilizados pelo criador são mantidos em biblioteca privada.

O repositório público não distribui PDFs, planilhas, tabelas de exercícios ou transcrições proprietárias do curso.

O mesmo princípio se aplica aos projetos externos utilizados como inspiração metodológica.

Consulte `course-library/README.md`, `references/THIRD_PARTY_INSPIRATION.md` e `LICENSE-STATUS.md`.

## 13. Contribuições

Contribuições são bem-vindas, especialmente nas áreas de:

- Segurança.
- Arquitetura local-first.
- Persistência de dados.
- Testes.
- Compatibilidade entre agentes.
- Usabilidade mobile.
- Acessibilidade.
- Qualidade dos workflows.

Consulte `CONTRIBUTING.md` antes de propor alterações.

Toda contribuição deve preservar a separação entre dados pessoais, materiais proprietários e código distribuível.

## 14. Licenciamento

O projeto ainda não possui licença open source selecionada.

A publicação pública no GitHub não concede automaticamente permissão para copiar, modificar ou redistribuir o conteúdo.

Consulte `LICENSE-STATUS.md` antes de reutilizar o código.

---

## Objetivo final

Construir uma ferramenta de acompanhamento físico que seja acessível, independente, segura e orientada por dados.

Uma ferramenta que ajude pessoas a treinar melhor, alimentar-se de maneira mais consciente e acompanhar sua evolução sem depender de soluções caras.

**Fitness Manager — sua evolução, documentada e orientada por dados.**
