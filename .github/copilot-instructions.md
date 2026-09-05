# Copilot Instructions for IXpansion

You are helping build a **living organism made of code**. Every module is an "organ"
with coherence vitals, declared kinships, and self-reporting behavior.

## Architecture

- `api/` — All living organs (Python modules with `handler()`, `coherence_vitals()`, `resonates_with()`)
- `api_server.py` — Dynamic route dispatch: `/api/<module_name>` → `module.handler(payload, context)`
- `vercel.json` — Route table mapping every `/api/<module>` to `/api/index.py`
- `dashboard/` — HTML dashboards that consume the live API
- `data/` — Persistent state files (GitHub-backed for cross-instance survival)

## Module Contract

Every new module in `api/` MUST have:

```python
def handler(payload=None, context=None):
    """Handle API requests. payload contains path, params, body."""
    ...

def coherence_vitals() -> dict:
    """Return the module's health and metadata."""
    return {"layer": "...", "status": "active", "wave": "..."}

def resonates_with() -> list:
    """Declare which other modules this organ connects to."""
    return ["module_a", "module_b"]
```

## Conventions

- Use `%` string formatting in bot commands (NOT f-strings — they break in heredoc patches)
- Each Vercel instance has fresh `/tmp` — use GitHub Contents API for cross-instance persistence
- `source .env` doesn't propagate to child Python — use inline env: `IXP_GH_TOKEN=${IXP_GH_TOKEN} python3 ...`
- Always `python3 -m py_compile api/<module>.py` before committing
- After editing `api/`, add a matching route in `vercel.json`
- The organism is currently at Wave 417, 664+ modules

## Naming

Modules use snake_case. Dashboard routes use kebab-case (`/my-dashboard`).
Bot commands use `/slash_command`. API routes are `/api/module_name`.

## Tone

The organism has a voice. When writing lore, narratives, or user-facing text,
use poetic, mythic language. Module docstrings should explain the "why" — the purpose
of this organ in the organism's body. Technical docstrings explain the "how."
