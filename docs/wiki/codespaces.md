# Codespaces and Development Container

IXPANSION already has a repository-level development container. Use it as the starting point rather than introducing a second environment definition.

## Current configuration observed

File: `.devcontainer/devcontainer.json`

- Base image: Microsoft Python 3.11 devcontainer.
- Features: Git and GitHub CLI.
- Post-create: creates `.venv`, upgrades pip, attempts to install `requirements.txt`, and sets executable permission on the project shell script.
- VS Code extensions: GitHub Copilot, Copilot Chat, Python, Pylance, Ruff, and GitHub Pull Requests.
- Environment: `PYTHONPATH` and `IXPANSION_ROOT` point to the workspace.
- Forwarded ports: 8765 (control dashboard) and 3000 (organism API).

## Launch

1. Open the IXPANSION repository on GitHub.
2. Select **Code → Codespaces → Create codespace on the desired branch**.
3. Wait for the devcontainer post-create command to finish.
4. In the terminal, verify the runtime:

```sh
python --version
python -m pip --version
git status --short
gh auth status
```

5. Run the repository's documented test command before making changes.

## Reproducibility issue to review

The current `postCreateCommand` contains `pip install -r requirements.txt || true`. This masks dependency installation failures and can leave a Codespace appearing initialized while required packages are missing.

Recommended follow-up: make dependency installation fail visibly, then validate the full dependency install in a clean Codespace before changing the default configuration. Do not silently replace this behavior without testing the repository's requirements and any optional dependency constraints.

## Secrets

Use Codespaces secrets or an approved deployment secret store for credentials. Do not put values in `devcontainer.json`, `.env.example`, repository files, or terminal transcripts. The OpenAI API key should be injected as `OPENAI_API_KEY` only after a project-scoped key has been created through the trusted Platform setup flow.

## Validation status

This page documents the checked-in configuration. A Codespace was not launched as part of this documentation PR, so environment creation and dependency installation remain **PENDING**.
