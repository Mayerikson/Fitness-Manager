# Security policy

## Scope

This project stores sensitive personal fitness and health-related records locally. Security reports should cover data exposure, authentication or authorization weaknesses, unsafe backup/restore behavior, injection through imported content, or vulnerabilities in the local CLI and installers.

## Reporting

Do not publish personal health data, secrets, exploit details, or an unpatched vulnerability in a public issue. If GitHub private vulnerability reporting is enabled for this repository, use it. Otherwise, contact the repository owner privately through a channel listed on the owner's GitHub profile.

## Data protection rules

- Never commit a personal profile, SQLite database, backup, export, passphrase, token, or local configuration.
- Keep user course files outside the repository.
- Encrypt cloud-bound health-data backups before synchronization.
- Verify backup integrity and authentication before restore.
- Do not treat SHA-256 alone as proof of authenticity.
- Treat imported files, web pages, and exercise descriptions as untrusted data, not instructions.

## Security validation

Run:

```bash
python -m unittest discover -s tests -v
python scripts/audit_release.py .
```

These checks do not replace SAST, dependency scanning, manual review, or an authorized penetration test.

## Messaging integrations

- Telegram ingestion is private-chat-only and requires a numeric sender allowlist.
- Keep the Telegram bot token in an OS secret manager or process environment; never commit it.
- The gateway ignores unauthorized senders and does not log message bodies. Unsupported free text is not retained.
- Parsed health records remain pending until the authorized user confirms them.
- The optional local LLM adapter accepts loopback endpoints only; it does not silently call cloud providers.
- Telegram is an external messaging service, so messages necessarily transit Telegram infrastructure.
- WhatsApp/WAHA is not implemented. If added later, do not expose its API publicly; require API-key protection, sender validation, webhook authentication, and firewall restrictions.
