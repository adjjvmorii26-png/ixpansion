# VS Code + GitHub Copilot — IXPANSION

## Open the project

```bash
git clone https://github.com/adjjvmorii26-png/ixpansion.git
cd ixpansion
git pull origin main
code ixpansion.code-workspace
# or: code .
```

When prompted: **Install Recommended Extensions** (Copilot, Python, Pylance, Ruff, Docker, GitHub PR).

## Sign in to Copilot

1. Command Palette → **GitHub Copilot: Sign In**
2. Complete browser auth (needs an active Copilot plan)

## Python env

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Select interpreter: `.venv/bin/python`

## Daily tasks

| Task | Action |
|------|--------|
| **ix: stable shell** | Project terminal |
| **ix: council** | AEGIS · HELIX · QUILL |
| **ix: local dashboard** | http://127.0.0.1:8765/ |
| **ix: snapshot** | Write `docs/LAB_STATUS.*` |

Or in terminal:

```bash
make shell
make council
make dashboard
```

Caption: `vscode · copilot · shell · dashboard`
