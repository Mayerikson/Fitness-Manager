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
