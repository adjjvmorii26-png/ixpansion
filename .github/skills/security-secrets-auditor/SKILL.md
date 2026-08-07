---
name: security-secrets-auditor
description: 'Audit IXPANSION for exposed secrets and unsafe configuration. Use when reviewing environment files, logs, CI workflows, API-key handling, dependencies, or security-sensitive documentation.'
argument-hint: '[security surface to audit]'
user-invocable: true
---

# Security Secrets Auditor

Find preventable secret exposure without weakening local development.

## Workflow

1. Inspect `.gitignore`, `.env.example`, CI workflows, code, tests, and documentation.
2. Search for hard-coded keys, tokens, credentials, private URLs, and accidental response logging.
3. Confirm `.env` is ignored and `.env.example` contains placeholders only.
4. Ensure shell environment values take precedence over local file values.
5. Check that errors do not include authorization headers or secret values.
6. If a credential may have been exposed, recommend revocation and replacement; never copy it into a report.
7. Run tests that cover environment loading and inspect tracked files with `git ls-files`.

Do not treat a placeholder value as a valid credential or add secret scanning tools without checking the project workflow first.
