# Supabase future synchronization roadmap

Supabase is intentionally not configured in v4.0. The authoritative database remains local SQLite; Google Drive receives verified backup snapshots through Google Drive for desktop, not live row-level synchronization.

If multi-device synchronization is later approved, implement it as a separate opt-in adapter:
1. Add stable UUID identifiers to every synchronizable record before the first remote sync.
2. Add `created_at`, `updated_at`, `source_device_id`, and a version/revision field where needed.
3. Use an outbox/inbox and idempotent upserts; never sync the SQLite database file itself between devices.
4. Define conflict policy per record type. Measurements and logs should be append-only; corrections should create new records rather than overwrite history.
5. Keep credentials outside the repository and local database, in the host's secret store/environment.
6. Use row-level security and least-privilege policies. Never expose service-role credentials to an agent prompt or client-side code.
7. Test offline edits, duplicate delivery, retries, clock skew, deletion handling, and restore before enabling production sync.
8. Preserve export/import and local-only operation if Supabase is unavailable.

No Supabase project, credentials, API calls, or remote synchronization are created by this package.
