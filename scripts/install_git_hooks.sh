#!/usr/bin/env bash
# Install versioned hooks via core.hooksPath (shared with the repo).
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
git config core.hooksPath hooks
chmod +x hooks/pre-commit hooks/commit-msg hooks/pre-push 2>/dev/null || true
echo "Installed: core.hooksPath=$(git config core.hooksPath)"
echo "Hooks: $(ls hooks/pre-commit hooks/commit-msg hooks/pre-push)"
