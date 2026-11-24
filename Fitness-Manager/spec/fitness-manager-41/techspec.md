# TechSpec — Fitness Manager 4.1

## Arquitetura
Local-first, Python standard library para operacao SQLite; dependencia opcional `cryptography` somente para criptografia autenticada de copia externa.

## Dados privados
`PROFILE_DEFAULT` aponta para `~/.fitness-manager/profile.json` ou `FITNESS_MANAGER_PROFILE`. O pacote contem apenas `data/profile.example.json`. A importacao ocorre somente quando a tabela profile esta vazia.

## Backup
Snapshot SQLite via API backup; SHA-256 para detectar corrupcao. Copia Drive usa envelope `FMENC1` + salt Scrypt + nonce + AES-256-GCM ciphertext. AAD vincula magic/salt/nonce. Passphrase vem de `FITNESS_MANAGER_BACKUP_PASSPHRASE` ou prompt interativo. Sem passphrase, a copia externa e bloqueada. Manifesto externo registra algoritmo, tamanho e hash do ciphertext.

## Restauracao
Validar manifesto/hash; descriptografar e validar tag GCM; executar `PRAGMA integrity_check`; criar copia pre-restore; restaurar em staging no mesmo volume e substituir com `os.replace`; validar novamente.

## Instalacao
Copiar para staging; mover destino anterior para pasta de backup versionada; promover staging; em falha, restaurar destino anterior. Nunca apagar instalacao anterior automaticamente.

## Governanca
MYK Spec-Driven Intelligence is maintained separately by the author. `governance/MODULE.md` defines the integration contract and preserves the internal MODULE.md convention. Root `SKILL.md` remains the portable Fitness Manager entry point.

## Riscos residuais
Banco ativo permanece plaintext; depende de criptografia de disco e controle de conta do sistema operacional. Variavel de ambiente pode ser lida por processos do mesmo usuario. Google Drive Desktop pode ainda nao ter concluido upload remoto; verificar status no cliente. Hash local nao prova identidade/aprovacao.
