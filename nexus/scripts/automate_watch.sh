#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
CYCLES="${1:-3}"
INTERVAL="${2:-8000}"
echo "NEXUS WATCH AUTOMATION  cycles=$CYCLES interval=${INTERVAL}ms"
node orchestrator/watch.js "$CYCLES" "$INTERVAL"
node metrics_export/status.js 2>/dev/null || true
