#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
echo "[ix] epoch ticket"
python lab/ops/epoch_ticket.py issue --scope "codespace:boot" --ttl 7200 || true
echo "[ix] helix constellation"
python lab/helix_bridge/probe.py || true
echo "[ix] lab smoke"
python lab/smoke_lab.py || true
echo "[ix] graft advisor"
python lab/ops/pr_graft_advisor.py || true
echo "[ix] boot complete"
