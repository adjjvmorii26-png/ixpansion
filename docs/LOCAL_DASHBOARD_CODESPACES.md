# Local VS Code dashboard + custom Codespaces

Everything runs **on your machine or in your Codespace** — no external dashboard host required.

## Local VS Code

```bash
cd /path/to/ixpansion
git fetch origin
git checkout lab/local-dashboard-codespaces

make dashboard
# open http://127.0.0.1:8765/
```

Or VS Code: **Tasks: Run Task** → **ix: local dashboard**.

The page shows live **AEGIS posture**, **HELIX next wave**, **QUILL headline**, and next moves via `/api/council`.

## Custom Codespaces (all-in-container)

1. Repo → **Code → Codespaces → New codespace** (uses `.devcontainer/devcontainer.json`).
2. Wait for postCreate (venv + deps).
3. Terminal:

```bash
make shell
make dashboard
```

Port **8765** auto-forwards and can open the browser to Local Control.

## Commands

| Command | Meaning |
|---------|---------|
| `make dashboard` | Local control UI + council API |
| `make council` | CLI council only |
| `make shell` | Stable project shell |

Caption: `local · control · codespace · dashboard`
