# Stable terminal for IXPANSION

One environment so `git`, `python`, co-pilots, and tests always see the same tree.

## Fastest path

```bash
cd /path/to/ixpansion
git pull origin main

# interactive project shell (prompt shows branch)
make shell
# or
source scripts/ix_shell.sh
```

Inside the shell:

| Command | Does |
|---------|------|
| `ix-council` | AEGIS · HELIX · QUILL brief |
| `ix-status` | `git status -sb` |
| `ix-pull` | `git pull --ff-only origin main` |
| `ix-pytest` | quick pytest |
| `ix-help` | reminder |

One-shot (no interactive shell):

```bash
make council
make env-check
```

## First-time venv (once)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# optional: pip install pytest ruff
```

`scripts/ix_shell.sh` auto-activates `.venv` or `venv` when present.

## VS Code / Cursor integrated terminal

1. Open the repo folder or workspace.
2. Terminal → New Terminal — settings inject `PYTHONPATH` and prefer `.venv`.
3. Command Palette → **Tasks: Run Task** → **ix: stable shell** or **ix: council**.

## Codespaces / remote

```bash
source scripts/ix_shell.sh
ix-council
```

Caption: `stable · shell · ix-council · make shell`
