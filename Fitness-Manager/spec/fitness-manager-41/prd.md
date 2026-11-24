# PRD — Fitness Manager 4.1

## Problema
A versao 4.0 armazena dados pessoais em profile.json distribuido no pacote, permite copia plaintext para pasta sincronizada e instala removendo a versao anterior. O projeto precisa incorporar governanca MYK e reduzir risco de exposicao/perda de dados.

## Objetivos
- Separar perfil privado do pacote distribuivel.
- Bloquear sincronizacao de backup em texto claro.
- Oferecer criptografia autenticada para backups do Drive.
- Preservar instalacoes anteriores durante upgrade.
- Integrar governanca MYK sem renomear arquivos de modulo do autor.
- Adicionar fluxos de substituicao e contingencia para treino.

## Fora de escopo
- Criptografia transparente do banco ativo.
- Supabase, autenticacao multiusuario ou sincronizacao bidirecional.
- Publicacao em lojas de aplicativos.
- Certificacao de seguranca ou pentest.

## Criterios de aceitacao
- CA-01: ZIP nao contem profile pessoal, banco, backup, chave ou segredo.
- CA-02: sem passphrase, copia para Drive nao gera arquivo plaintext.
- CA-03: backup criptografado valida SHA-256 e tag AES-GCM.
- CA-04: senha incorreta/adulteracao impede restauracao.
- CA-05: restauracao cria copia pre-restore e usa arquivo staging validado.
- CA-06: instalador preserva versao anterior e restaura em falha.
- CA-07: MYK e nomenclatura MODULE/SKILL sao documentados sem renomear fontes.
- CA-08: workflows de substituicao e contingencia estao disponiveis.
