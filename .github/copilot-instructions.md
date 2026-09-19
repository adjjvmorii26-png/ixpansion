# Copilot Instructions for IXPANSION

You are helping build a **living organism made of code**. Every module is an "organ"
with coherence vitals, declared kinships, and self-reporting behavior.

**Current frontier:** Wave **769+** (hush_compass 768, void_index 769).
**Co-pilots on main:** AEGIS (guard) · HELIX (grow) · QUILL (remember) alongside **ALEPH**.

## Architecture

- `api/` — Living organs (`handler`, `coherence_vitals`, `resonates_with`)
- `api_server.py` / `api/index.py` — Route dispatch `/api/<module>`
- `lab/ops/copilots/` — AEGIS · HELIX · QUILL (`make council`)
- `lab/ops/dashboard_server.py` — Local Control UI (`make dashboard` → :8765)
- `scripts/ix_shell.sh` — Stable terminal (`make shell`)
- `dashboard/` — HTML surfaces (including `local_control.html`)
- `data/` — Persistent organ state
- `.vscode/` — Copilot + Python workspace pack

## Dual-track doctrine (do not break)

| Track | Purpose |
|-------|---------|
| **ALEPH / main** | Full monorepo CI, organism velocity |
| **lab/** | Path-filtered experiments; lab gates ≠ full ALEPH suite |

- Prefer small, mergeable PRs (`lab/*` branches).
- Do not treat external scanner (GHAS AI findings) noise as organism gate failures.
- Silence is the product surface for @CoodingLooop captions (text-only; no audio requirement).

## Module contract

Every new organ in `api/` MUST expose:

```python
def handler(req=None) -> dict: ...
def coherence_vitals() -> dict: ...  # include wave, name, ok
def resonates_with() -> list: ...
```

Wave pattern: `api/waveNNN_slug.py` + `tests/test_waveNNN_slug.py` + optional `lab/WAVE_NNN_*.md`.

## Local commands (keep green)

```bash
make shell          # stable terminal
make council        # AEGIS · HELIX · QUILL
make dashboard      # http://127.0.0.1:8765/
make snapshot       # docs/LAB_STATUS.*
python -m pytest tests/test_copilots.py tests/test_wave769_void_index.py -q
```

## Conventions

- `python3 -m py_compile` new modules before commit
- Conventional commits: `feat(waveN):`, `fix:`, `chore:`, `feat(lab):`
- Prefer stdlib for lab ops; avoid new heavy deps without need
- Never leak void_index payloads (keys only; `payload: None`)

## GitHub Copilot Coding Agent

When implementing assigned issues:
1. Read this file + `AGENTS.md` + `docs/DUAL_TRACK.md` if present
2. Run `make council` or equivalent mentally: guard → grow → remember
3. Keep changes path-scoped; open PR against `main` from `lab/...`
4. Include tests for new waves; do not expand CI surface without need

## Tone

Poetic lore in user-facing captions is welcome; code stays precise and testable.
