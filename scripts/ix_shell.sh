#!/usr/bin/env bash
# IXPANSION stable project terminal
# Usage:  source scripts/ix_shell.sh
#    or:  ./scripts/ix_shell.sh          (starts a subshell)
#    or:  make shell
set -euo pipefail

_IX_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." && pwd)"
cd "$_IX_ROOT"

if [[ -d "$_IX_ROOT/.venv" ]]; then
  # shellcheck disable=SC1091
  source "$_IX_ROOT/.venv/bin/activate"
elif [[ -d "$_IX_ROOT/venv" ]]; then
  # shellcheck disable=SC1091
  source "$_IX_ROOT/venv/bin/activate"
else
  echo "[ix] no .venv yet — create with: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
fi

export PYTHONPATH="${_IX_ROOT}${PYTHONPATH:+:$PYTHONPATH}"
export IXPANSION_ROOT="$_IX_ROOT"
export PYTHONDONTWRITEBYTECODE=1

if ! command -v python >/dev/null 2>&1 && command -v python3 >/dev/null 2>&1; then
  alias python=python3 2>/dev/null || true
fi

_ix_branch() {
  git -C "$_IX_ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "detached"
}
export PS1='\[\e[36m\]ix\[\e[0m\]:\[\e[33m\]$(_ix_branch)\[\e[0m\] \w \$ '

ix-council()  { python "$_IX_ROOT/lab/ops/copilots/council.py" "$@"; }
ix-status()   { git -C "$_IX_ROOT" status -sb; }
ix-pull()     { git -C "$_IX_ROOT" pull --ff-only origin main; }
ix-pytest()   { python -m pytest tests/ -q --tb=line "$@"; }
ix-snapshot() { python "$_IX_ROOT/lab/ops/status_snapshot.py" "$@"; }
ix-dashboard() {
  if [[ ! -f "$_IX_ROOT/lab/ops/dashboard_server.py" ]]; then
    echo "[ix] dashboard_server.py missing — merge tooling PR or pull latest"
    return 1
  fi
  echo "[ix] Local Control → http://127.0.0.1:8765/"
  PYTHONPATH="$_IX_ROOT" python "$_IX_ROOT/lab/ops/dashboard_server.py" --host 127.0.0.1 --port 8765
}
ix-help() {
  cat <<'H'
IXPANSION stable shell
  ix-council [--json]   AEGIS · HELIX · QUILL
  ix-snapshot           write docs/LAB_STATUS.*
  ix-dashboard          Local Control UI :8765
  ix-status             short git status
  ix-pull               git pull --ff-only origin main
  ix-pytest [args]      quick pytest
  make shell | council | dashboard
H
}

if [[ "${-}" == *i* ]] || [[ "${IX_SHELL_BANNER:-1}" == "1" ]]; then
  echo "── IXPANSION stable terminal ──"
  echo "  root:  $_IX_ROOT"
  echo "  py:    $(command -v python 2>/dev/null || command -v python3)"
  echo "  branch:$(_ix_branch)"
  echo "  tip:   ix-help · ix-council · make shell"
  echo "───────────────────────────────"
fi

if [[ "${BASH_SOURCE[0]:-$0}" == "${0}" ]]; then
  export IX_SHELL_BANNER=0
  exec bash --rcfile <(echo "source '$_IX_ROOT/scripts/ix_shell.sh'") -i
fi
