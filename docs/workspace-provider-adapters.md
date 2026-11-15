# Workspace Provider Adapters v1

**Status:** implemented behind explicit runtime configuration on `feat/workspace-provider-adapters-v1`; not activated against production providers.

## Scope

- `NotionDatabaseAdapter`: idempotent page upsert into an existing configured Notion database.
- `GoogleDriveMetadataAdapter`: idempotent Drive metadata upsert using collision-resistant private `appProperties` hashes.
- Both implement the existing runner contract and perform read-after-write verification.
- Standard-library HTTP transport only; bounded 1–20 second timeout and 2 MB response cap.

## Runtime configuration

- `NOTION_API_TOKEN`: Notion integration token.
- `IXPANSION_NOTION_DATABASE_ID`: existing database ID writable by that integration.
- `IXPANSION_NOTION_TITLE_PROPERTY`: optional title property name; defaults to `Name`.
- `GOOGLE_DRIVE_ACCESS_TOKEN`: Google OAuth access token with least-privilege Drive metadata scope.
- `IXPANSION_DRIVE_PARENT_ID`: optional folder ID used only when creating a new file.

Tokens are read only from process environment. Never put them in source, event payloads, provider metadata, or logs. Access tokens expire; token refresh is delegated to the host runtime/secret manager and is not implemented here.

## Event payload

For `upsert_artifact`, supply `artifact_id` or `title`, plus `source_revision`. Optional fields: HTTP(S) `url`, and Drive-only `mime_type`. Drive lookups search across accessible My Drives and Shared Drives (`corpora=allDrives`). The event idempotency key is hashed into Drive's private appProperties to avoid truncation collisions. A replay queries by that marker and updates the same remote artifact. Multiple matches are quarantined.

## Required Notion database schema

The configured database must already exist, be shared with the integration, and have:
- a title property (default name `Name`; override with `IXPANSION_NOTION_TITLE_PROPERTY`),
- rich-text property `IXPANSION Key`,
- rich-text property `Source Revision`,\n- optional URL property `Artifact URL` if event payloads include `url`.

The adapter does not create or mutate the database schema.

## Deliberate limits

- Drive writes metadata/pointers only; it does not upload or replace file bytes.
- Existing Drive files are not moved between folders.
- No sharing/permission changes, deletion, arbitrary block append, or external publication.
- No token refresh, scheduled daemon, automatic discovery, or production activation.
- 429/5xx and transport failures are retryable; 4xx, malformed responses, and duplicate-match states are quarantined.
- HTTP errors are sanitized; raw authorization headers and tokens are never returned in receipts.

## Verification

```bash
python -m unittest tests.test_workspace_sync_providers tests.test_workspace_sync_outbox tests.test_workspace_sync_shadow_twin -v
```

Tests use a deterministic fake HTTP transport. They do not call Notion or Google.
