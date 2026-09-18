# VS Code + GitHub Copilot — IXPANSION workspace

This repo ships a ready `.vscode/` pack so VS Code and Copilot are fully usable on this project.

## 1. Install VS Code (local machine)

- Download: https://code.visualstudio.com/
- Optional CLI: in VS Code → Command Palette → **Shell Command: Install 'code' command in PATH**

## 2. Open this project

```bash
git clone https://github.com/adjjvmorii26-png/ixpansion.git
cd ixpansion
code ixpansion.code-workspace
# or: code .
```

When prompted: **Install Recommended Extensions**  
That installs Copilot, Copilot Chat, Python, Pylance, Ruff, Docker, GitHub PR, GitLens.

## 3. Activate GitHub Copilot (required once)

1. Sign in to GitHub in VS Code (Accounts icon, bottom-left).
2. Command Palette → **GitHub Copilot: Sign In** (or open Copilot Chat and follow the link).
3. Accept permissions. Copilot needs an active plan (Individual / Business / student, etc.).
4. Confirm: status bar shows Copilot icon; typing in a `.py` file suggests completions.

**Copilot Chat:** `Ctrl+Alt+I` (Windows/Linux) or `Ctrl+Cmd+I` (macOS).

## 4. Python environment

Command Palette → **Tasks: Run Task** → **venv: create + install**

Or:

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt   # if present
pip install pytest ruff
```

Select interpreter: **Python: Select Interpreter** → `.venv`.

## 5. What this pack enables

| Feature | Config |
|--------|--------|
| Inline Copilot completions | `settings.json` → `github.copilot.enable` |
| Copilot Chat / agent tools | Chat settings + Copilot Chat extension |
| Format on save (Ruff) | `[python]` formatter |
| Pytest discover + debug | `settings` + `launch.json` |
| One-click tests | Task **pytest: quick** |
| PR queries (lab branches) | GitHub Pull Requests extension |
| `PYTHONPATH` for `api/` + `lab/` | terminal + launch env |

## 6. Troubleshooting

| Symptom | Fix |
|--------|-----|
| No completions | Sign in; check Copilot subscription |
| Wrong Python | Select `.venv` interpreter |
| Import errors for `api.*` | Reopen terminal after settings load |
| Chat missing | Install **GitHub Copilot Chat**; reload window |

## Caption

`vscode · copilot · venv · pytest · lab-ready`
