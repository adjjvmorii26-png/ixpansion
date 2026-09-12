# AGENTS.md — IXPANSION conventions

IXPANSION is a living monorepo: ~1000 Python organs under `api/` with an
evented server (serverless entry `api/index.py`), a GitHub Pages dashboard
hub, and a 1400+ test suite. The organism evolves in numbered "waves".

## Wave pattern (how to add a wave organ)
- `api/waveNNN_name.py` — module contract: `handler(req) -> dict`,
  `coherence_vitals() -> dict` (include `wave`), and optionally
  `resonates_with()`. Functions prefer `_load`/`_save` against
  `data/waveNNN_name.json` living state.
- `api/index.py` — wire `/name` + `/api/name` dispatch (match the
  existing wave blocks; keep them grouped).
- `data/waveNNN_name.json` — seed state (do not leave test garbage).
- `dashboard/name.html` — dark hex-aesthetic page calling
  `/api/name?action=...` (API prefix `''`, fetch relative paths).
- `tests/test_waveNNN.py` — cover every action + `coherence_vitals`.
- `README.md` wave table + `CHANGELOG.md` entry + version bump
  (`pyproject.toml`, `omega_fractal_engine/pyproject.toml`,
  `CITATION.cff` — `tests/test_release_metadata.py` verifies they match).

## Rules
- Never break the module contract; tests assert it in CI (`ci.yml`).
- Keep data JSON mutation light; tests mutate drifting state harmlessly.
- Run `python3 -m pytest tests/test_waveNNN.py -q` after changes; full
  sweep takes ~25 min (`tests/`, ~1400 tests).
- Slow filesystem-wide scans (e.g. `api/constellation.py`) must stay
  under the 30s subprocess sandbox limit — use token lookup, not
  substring scans.
- Commits: conventional (`feat(waveN): ...`, `fix: ...`, `chore: ...`).
  Push to `main`; deploys are automated (Pages + Cloudflare tunnel).
