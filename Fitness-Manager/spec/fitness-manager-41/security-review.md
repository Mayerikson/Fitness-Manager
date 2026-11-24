# Security findings — 4.1

## SEC-01 — Perfil pessoal no pacote
Severidade: High para distribuicao. Correcao: perfil removido do ZIP; importacao externa.

## SEC-02 — Backup plaintext no Drive
Severidade: High para dados de saude. Correcao: AES-256-GCM; sem segredo, sincronizacao bloqueada.

## SEC-03 — Segredo de backup
Risco residual: variavel de ambiente e acessivel a processos do mesmo usuario. Mitigacao atual: nao armazenar em config, chat ou repositorio. Recomendacao futura: Windows Credential Manager/macOS Keychain/libsecret.

## SEC-04 — Banco ativo plaintext
Risco residual: arquivo SQLite legivel por quem tiver acesso ao perfil do sistema. Mitigacao: diretorio no home, ACL do usuario e full-disk encryption. Criptografia transparente do banco ativo permanece fora do escopo.

## SEC-05 — Integridade do manifesto
SHA-256 detecta corrupcao acidental; nao autentica manifesto. AES-GCM autentica ciphertext e conteudo descriptografado, mas nao autentica aprovacao humana.

## SEC-06 — Instalador destrutivo
Correcao: staging e preservacao de instalacao anterior.

## Status
Findings corrigidos no codigo local e submetidos a testes automatizados; revisao de instalacao em plataformas reais e `NOT_RUN`. Nenhum pentest ou scanner externo foi executado.
