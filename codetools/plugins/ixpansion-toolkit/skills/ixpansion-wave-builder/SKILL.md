---
name: ixpansion-wave-builder
description: Build a new evolution "wave" of living organs for the IXpansion organism (api/*.py modules) — scaffold organs, wire routes, sync manifests, bump versions, push to GitHub, deploy to Vercel. Use when the user asks to continue/refine IXpansion, add wave N, or create new living modules.
---

# IXpansion Wave Builder

IXpansion is a living organism of self-reporting Python modules. Each new
"wave" adds 5-8 organs (one file = one organ) and ships them to production.
The work is repetitive but laden with hidden failure modes; the checklist in
`references/checklist.md` enumerates the exact order and the critical bugs.

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

## Workflow (summary)

1. Write the organs + tests.
2. Wire: `gateway/intent.py` → `api/coherence_regulator.py` → `vercel.json`
   (API route before dashboard route) → `api_server.py` alias (with `return`)
   → `api/index.py` endpoint (with the `q = {}` query parse).
3. Bump `VERSION`/`WAVE`/`WAVE_NAME` in `api_server.py`,
   `api/organism_ontology.py`, `dashboard/shared.js`, `pyproject.toml`,
   `CITATION.cff`. Create `dashboard/<wave>.html` (monospace terminal
   aesthetic, include `<script src="/shared.js">`).
4. Update `CHANGELOG.md` + `REVELATIONS.md`.
5. `git add -A && git commit && git push origin main`.
6. Deploy: `vercel --yes --prod --token <vcp token>`.
7. Verify: `curl -s https://ixpansion.vercel.app/health` shows the new wave.

Use `scripts/` helpers to scaffold an organ or bump versions instead of
hand-editing. Full step-by-step in `references/checklist.md`.
