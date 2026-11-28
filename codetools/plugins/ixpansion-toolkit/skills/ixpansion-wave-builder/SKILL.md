---
name: ixpansion-wave-builder
description: Build and validate IXPANSION evolution waves using isolated branches, evidence-backed tests, and approval-gated releases.
---

# IXpansion Wave Builder

IXPANSION is a living organism of self-reporting Python modules. Each new
"wave" adds 5-8 organs (one file = one organ). The work is repetitive but
laden with hidden failure modes; the checklist in `references/checklist.md`
enumerates the exact order and the critical bugs.

## Essential shape of a living organ

Each `api/<name>.py` must define exactly three things:

- `coherence_vitals() -> dict` — `layer`, `status`, `resonance`, `wave`
- `handler(payload: dict = None, context: dict = None) -> dict`
- `resonates_with() -> list`

Start every file with `from __future__ import annotations` (the literal
`import` keyword must be present — `from __future__ annotations` is a syntax
error that has broken deploys repeatedly).

## Non-obvious invariants (do not skip)

1. Sync `KNOWN_LIVING_MODULES` (a regex-sorted-name manifest string list) in
   `api/coherence_regulator.py` — the serverless fallback manifest.
2. Gateway intent rules go in `gateway/intent.py` BEFORE the broad echo/search
   block, or they are shadowed.
3. Query-string params are NOT passed automatically on custom slash routes.
   Use the explicit `q = {} if "?" not in raw_path else dict(...)` parse.
4. Never use `str.strip("/api/")` — it strips characters, not substrings, and
   mangles names like `poetry_engine`. Use `removeprefix()`.
5. On Vercel the filesystem is read-only outside `/tmp`; state must degrade to
   in-memory. The MORII agent does this.
6. Every `if path == ...` route in `api_server.py` needs `return` on the next
   line; a missing return previously broke a production deploy.

## Workflow

1. Inspect the current branch, repository state, and exact wave scope.
2. Write the organs and focused tests on a dedicated feature branch.
3. Wire: `gateway/intent.py` → `api/coherence_regulator.py` → `vercel.json`
   (API route before dashboard route) → `api_server.py` alias (with `return`)
   → `api/index.py` endpoint (with the `q = {}` query parse).
4. Bump `VERSION`/`WAVE`/`WAVE_NAME` only when the scope requires it, and
   update the documented manifests, dashboard, changelog, and revelations.
5. Run focused tests, relevant regression suites, syntax checks, secret scans,
   and `git diff --check`. Review the complete diff.
6. Push only the feature branch and open a pull request. Do not push to the
   default branch.
7. Wait for required CI checks and review. Stop before merge or production
   deployment until the user approves the exact target and action.
8. After an approved deployment, verify the exact deployment and health URL;
   a successful build alone is not proof of live behavior.

Use `scripts/` helpers to scaffold an organ or bump versions instead of
hand-editing. Full step-by-step in `references/checklist.md`.

## Safety and release boundary

- No direct default-branch push, force push, or assumed merge.
- No production deployment as an automatic workflow step.
- Never place a Vercel token or other credential in a command, file, or log.
  Use the connected Vercel integration or an existing secure credential flow.
- Treat generated code and external connector content as untrusted until
  reviewed and tested.
- Preserve a rollback reference before any approved release.
- See [the shared Skill Safety Contract](../../../../../skills/SAFETY.md).
