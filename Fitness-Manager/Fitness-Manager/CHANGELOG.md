# Changelog

## 5.1.0-beta.4 — UX MVP: resumo de treino concluído
- Adicionada especificação da tela contextual de conclusão do treino.
- Definidos critérios para duração, conclusão parcial, substituições e comparações com sessões anteriores.
- Incluídas regras para compartilhamento sem exposição de dados sensíveis por padrão.
- Mantida a navegação principal com três áreas: Hoje, Academia e Evolução.
- Esta versão atualiza especificações de UX; não representa a implementação do PWA.


## 5.1.0-beta.3 — parser de linguagem natural e UX MVP
- Adicionada regressão para as sete frases comuns relatadas pelo usuário.
- Normalização de acentos e pontuação periférica antes da interpretação.
- Conversão de números por extenso entre 101 e 199 sem alterar nomes de exercícios.
- Preservação de acentos e grafia original dos nomes de exercícios por mapeamento de offsets.
- Adicionada especificação UX de três telas: Hoje, Modo Academia e Dashboard.
- README principal em português brasileiro e README.en.md como documentação complementar.
- Pacote de publicação com estrutura plana, sem diretório duplicado nem caches Python.

## 5.1.0-beta.2 — confiabilidade da ingestão
- Rejeição de medidas, séries, repetições e quantidades alimentares inválidas.
- Tratamento de falhas SQLite durante confirmação no Telegram.
- Isolamento de falhas por atualização e avanço do offset de polling.
- Data atual como padrão para medidas sem data explícita.
- Auditoria de distribuição passa a sinalizar `__pycache__`.

## 5.1.0-beta.1 — entrada multimodal
- Requisitos de entrada por texto e áudio.
- Transcrição local opcional com faster-whisper.
- Recebimento de áudio no Telegram com prévia e confirmação.
- Parser determinístico para registros comuns em português.

## 5.0.0-beta.1 — estabilização e base do produto
- Pacote Python modular e CLI.
- Banco SQLite, histórico e auditoria.
- Backup, integridade e restauração.
- Cópias criptografadas opcionais para sincronização com Google Drive.
- Testes automatizados e CI inicial.

## 4.3.0 — preparação do handoff público
- Separação de dados pessoais e materiais privados.
- Documentação de produto, arquitetura e segurança.
- Entrada portátil `SKILL.md` e módulos internos `MODULE.md`.
