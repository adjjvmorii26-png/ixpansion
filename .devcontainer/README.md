# IXpansion Codespace

A pre-configured GitHub Codespace for the IXpansion organism.

## What's included

- Python 3.12 + pip
- Node.js LTS
- GitHub CLI + Git
- VS Code extensions: Python, Pylance, Ruff, Docker, GitHub Actions, YAML, Black

## Setup

The `setup.sh` script runs automatically on container creation:
1. Installs `requirements.txt` + `pyvis`, `graphviz`, `httpx`, `pyyaml`
2. Creates sandbox directories (`data/sandbox*`, `output/sandbox`)
3. Verifies `.env.sandbox` keys (or warns to copy from `.env.sandbox.example`)
4. Runs organism velocity check

## Quick commands

```bash
python3 lab/ops/velocity_burst.py        # organism health
python3 -m pytest tests/ -q --tb=no       # full test suite (~1400 tests)
python3 scripts/load_sandbox.py --check   # verify sandbox keys
python3 scripts/scaffold_organ.py -w 763 -n new_organ -a status,ping   # new wave organ
python3 scripts/bump_versions.py --version 4.120.0 --wave 763 --name "Organ Name"  # bump version
```

## Ports

| Port | Service |
|------|---------|
| 8000 | API Server |
| 8080 | Dashboard (auto-opens) |
| 5173 | Dev Server (auto-opens) |

## Sandbox keys

- Real keys: `.env.sandbox` (git-ignored)
- Template: `.env.sandbox.example` (safe to commit)
- Loader: `python3 scripts/load_sandbox.py`

## Sandbox directories

- `data/sandbox` — isolated data
- `data/sandbox_state` — organism state
- `data/sandbox_logs` — debug logs
- `output/sandbox` — output artifacts
