# Fitness Manager

### Seu treinamento, sua alimentação e sua evolução — organizados por dados.

**Versão:** `5.1.0-beta.5`  
**Idioma principal:** português brasileiro  
**Arquitetura:** local-first, model-portable  
**Estágio:** beta pessoal, com CLI e integração opcional ao Telegram

O Fitness Manager é um sistema pessoal para registrar e acompanhar musculação, alimentação, medidas corporais, recuperação e corrida de rua até 15 km. Os registros e cálculos básicos funcionam localmente, sem exigir conexão com uma LLM ou API paga.

> **Registrar. Confirmar. Acompanhar. Evoluir.**

## Estado real do projeto

### Implementado

- Banco SQLite local e CLI em Python.
- Registro e consulta de perfil, peso, medidas, alimentação, treinos, corridas e decisões de planejamento.
- Histórico de eventos, auditoria e prevenção de duplicidade na ingestão.
- Backup local, verificação de integridade e restauração com cópia de segurança prévia.
- Cópia criptografada AES-256-GCM para pasta sincronizada do Google Drive, quando configurada com a dependência e senha necessárias.
- Gateway Telegram opcional, com lista de remetentes autorizados, parser determinístico, confirmação antes de gravar e isolamento de falhas por mensagem.
- Recebimento de áudio no Telegram e transcrição local opcional com faster-whisper; o áudio é temporário e a transcrição exige confirmação.
- Workflows e instruções portáteis para hosts compatíveis com Agent Skills.
- Testes automatizados e workflow de CI no GitHub Actions.

### Ainda não implementado

- PWA, painel web em localhost e interface mobile.
- Aplicativos nativos Android e iOS.
- Captura de áudio pelo navegador ou aplicativo próprio.
- Integração WhatsApp/WAHA.
- Motor automático de equivalência biomecânica para substituição de exercícios.
- Agentes autônomos em execução contínua: os arquivos em `agents/` são instruções especializadas, não processos independentes.
- Sincronização Supabase e produto multiusuário.

Consulte `docs/HANDOFF.md` e `docs/ROADMAP.md` para o estado detalhado.

## Princípios

- **Local-first:** os dados pessoais ficam no dispositivo do usuário, em SQLite.
- **Sem LLM para registros comuns:** parser, validação, cálculos, CLI e persistência são determinísticos.
- **LLM opcional:** perguntas analíticas podem usar um endpoint local compatível, quando configurado.
- **Confirmação humana:** mensagens interpretadas são apresentadas para revisão antes de criar registros de saúde.
- **Portabilidade:** instruções em Markdown são separadas do motor Python e do banco.
- **Rastreabilidade:** dados medidos, informados, calculados, estimados e desconhecidos devem ser distinguidos.
- **Segurança proporcional:** alterações em dados, backup, criptografia, autenticação e sincronização exigem testes e revisão.

## Requisitos

- Python 3.10 ou superior.
- Windows, macOS ou Linux.
- Para usar Telegram: conexão com a internet e um bot criado no BotFather.
- Para transcrição local de voz: dependências opcionais de `requirements-audio.txt`; o modelo é baixado na primeira utilização e executado localmente.

As operações locais básicas não exigem Node.js, banco externo, chave de API ou assinatura de IA.

## Instalação rápida

Na raiz do repositório:

```bash
python scripts/fitness_manager.py init
python scripts/fitness_manager.py report
```

Consultar o histórico:

```bash
python scripts/fitness_manager.py history --limit 50
```

Ver todos os comandos disponíveis:

```bash
python scripts/fitness_manager.py --help
```

### Instalar a Agent Skill

O ponto de entrada portátil é o `SKILL.md` da raiz. Use as instruções específicas em `adapters/` para Claude Code, Codex, Qwen Code e outros hosts compatíveis.

- `SKILL.md`: entrada reconhecida pelos hosts compatíveis.
- `MODULE.md`: convenção intencional para módulos internos de governança; esses arquivos são carregados explicitamente e não são Skills auto-descobertas.

Um modelo de IA isolado não é, por si só, um host de Skills. É necessário um ambiente com acesso aos arquivos e, para executar o motor local, capacidade de rodar Python.

## Registros sem IA

Os exemplos abaixo usam dados fictícios:

```bash
python scripts/fitness_manager.py weigh-in --weight 73.4
python scripts/fitness_manager.py measure --kind waist --value 84 --unit cm --method "horizontal at navel"
python scripts/fitness_manager.py food --meal lunch --food rice --quantity-g 150
python scripts/fitness_manager.py workout --session A --exercise "Supino reto" --sets 3 --reps 12 --load-kg 20
python scripts/fitness_manager.py run --distance-km 4 --duration-min 30
```

Os valores nutricionais não são inventados: calorias e macronutrientes permanecem desconhecidos se não forem fornecidos ou consultados em uma fonte de composição confiável.

## Telegram: registro por mensagem

O gateway aceita comandos estruturados e algumas frases comuns em português. Exemplos fictícios:

```text
peso 72 quilos.
minha cintura é 84 centímetros
corri 4 quilômetros em 30 minutos
fiz uma corrida de quatro quilômetros em trinta minutos
fiz supino reto, três séries de doze repetições com vinte quilos.
```

O parser normaliza acentos e pontuação periférica, reconhece números por extenso em campos numéricos e preserva o nome original do exercício. Mensagens não reconhecidas ou ambíguas não são gravadas como dados de saúde.

Configure localmente `FITNESS_MANAGER_TELEGRAM_BOT_TOKEN` e `FITNESS_MANAGER_TELEGRAM_ALLOWED_USER_ID`. Nunca publique esses valores.

Inicie o gateway:

```bash
python scripts/telegram_gateway.py
```

O bot apresenta uma prévia e exige confirmação explícita antes de persistir. Telegram precisa de internet para transportar mensagens, mas o parsing e a gravação são locais e não consomem tokens de LLM.

### Transcrição local de áudio

Instale as dependências opcionais:

```bash
pip install -r requirements-audio.txt
```

O primeiro uso baixa os pesos do modelo selecionado. Depois da instalação/cache, a transcrição ocorre localmente. O áudio temporário é removido após o processamento. A transcrição e a interpretação precisam ser confirmadas antes de salvar.

## Backup e restauração

Criar backup local:

```bash
python scripts/fitness_manager.py backup
```

Restaurar um backup:

```bash
python scripts/fitness_manager.py restore --from "CAMINHO_DO_BACKUP.sqlite"
```

O banco pessoal fica em `~/.fitness-manager/` (ou no caminho definido por `FITNESS_MANAGER_HOME` / `FITNESS_MANAGER_DB`). Não coloque banco, perfil, backups, tokens ou arquivos privados no Git.

Para sincronizar cópias com uma pasta do Google Drive, use a criptografia AES-256-GCM e configure `FITNESS_MANAGER_BACKUP_PASSPHRASE` no ambiente local. O sistema bloqueia cópia em nuvem sem criptografia configurada. SHA-256 detecta corrupção acidental; não é assinatura digital nem proteção contra administrador local malicioso.

## Estrutura do repositório

```text
Fitness-Manager/
├── .github/workflows/       # CI
├── agents/                  # instruções especializadas
├── adapters/                # instalação por host
├── docs/                    # PRD, arquitetura, segurança e handoff
├── fitness_manager/         # motor Python e SQLite
├── governance/              # módulos internos MODULE.md
├── references/              # proveniência e referências
├── scripts/                 # CLI, gateway e auditoria
├── tests/                   # testes automatizados
├── workflows/               # procedimentos delimitados
├── SKILL.md                 # entrada portátil
└── VERSION
```

## Testes e auditoria

```bash
python -m unittest discover -s tests -v
python scripts/audit_release.py .
python scripts/fitness_manager.py --help
```

O CI está configurado para Python 3.10–3.13. A aprovação local não substitui a execução do workflow remoto após o push.

## UX: três telas principais, não dezenas

A direção de experiência do usuário é responder a três perguntas:

1. **O que faço hoje?** — tela Hoje, com treino planejado, refeições, follow-ups e ações rápidas.
2. **Como executo e registro?** — modo Academia, com exercício atual, vídeo verificado, séries, cargas, substituições e entrada por texto/voz com confirmação.
3. **Estou evoluindo?** — dashboard com peso, cintura, adesão, força, corridas e tendências.

Essa é uma proposta de UX para o futuro PWA, não uma interface já implementada. Consulte `docs/UX-MVP.md`.

## Privacidade e segurança

- O repositório público não deve conter dados pessoais, SQLite, backups, tokens, `.env`, arquivos de áudio ou materiais proprietários de cursos.
- Mensagens do Telegram passam pela infraestrutura do Telegram; o processamento local não torna o transporte privado de ponta a ponta.
- O sistema não é dispositivo médico e não substitui profissionais de saúde.
- Consulte `SECURITY.md` e `docs/SECURITY-MODEL.md`.

## Materiais de terceiros e licença

Materiais privados do curso Leandro Twin não são distribuídos neste repositório. O catálogo privado de exercícios e os mapeamentos de vídeos devem permanecer fora do repositório público, salvo autorização expressa dos titulares.

O projeto ainda não selecionou uma licença open source. Consulte `LICENSE-STATUS.md`. A visibilidade pública do GitHub não concede automaticamente direitos de reutilização.

## Roadmap

1. Estabilizar parser, Telegram, persistência, testes e CI.
2. Construir PWA mobile-first com as três telas essenciais.
3. Adicionar modo academia e biblioteca de mídia verificada.
4. Validar com usuários beta e medir adesão/usabilidade.
5. Avaliar sincronização multiusuário e monetização somente após validação.

**Fitness Manager — sua evolução, documentada e orientada por dados.**


### UX especificada nesta versão

A especificação inclui uma tela contextual de conclusão do treino, com duração baseada em registros, distinção entre exercícios concluídos/parciais/não realizados, substituições e compartilhamento opcional com dados sensíveis ocultos por padrão. O PWA ainda não foi implementado.


## Continuidade do projeto


Novo agente ou desenvolvedor?

Leia primeiro o [[PROJECT-HANDOFF.md](PROJECT-HANDOFF.md](https://github.com/Mayerikson/Fitness-Manager/blob/main/Fitness-Manager-PROJECT-HANDOFF.md)).
Ele contém o contexto, as decisões arquiteturais,
o estado atual e o roadmap do Fitness Manager.
