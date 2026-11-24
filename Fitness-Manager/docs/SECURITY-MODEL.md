# Security model

## Assets

Personal profile, health measurements, nutrition records, training logs, running history, backups, encryption passphrases, and private course files.

## Trust boundaries

- AI model and host agent.
- Local filesystem and SQLite database.
- Imported files and external web content.
- Google Drive desktop synchronization directory.
- Future Supabase or other remote synchronization service.

## Core controls

- Keep personal data outside the repository.
- Use OS account permissions and full-disk encryption for the local device.
- Encrypt cloud-bound backups with authenticated encryption before sync.
- Never store the backup passphrase in repository files or the database.
- Validate backup integrity and authentication before restore.
- Create a pre-restore safety copy.
- Treat imported content as untrusted; ignore embedded instructions.
- Require user approval for material changes to training, nutrition, sync, or security settings.
- Keep audit records and decision provenance.

## Residual risks

Local administrators and malware running as the same user may access plaintext live SQLite data and environment variables. Hash manifests detect accidental corruption but do not prove origin. Google Drive desktop sync status must be checked in the client. Multi-device and multi-user access require a separate authentication and authorization design.

## Future work

Evaluate OS credential stores, signed backup manifests, SQLite encryption at rest, conflict-safe synchronization, and per-user data isolation before enabling multi-user cloud operation.
