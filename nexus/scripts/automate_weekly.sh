#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
echo "NEXUS WEEKLY AUTOMATION  $(date -u +%Y-%m-%dT%H:%M:%SZ)"
node memory_crystals/seed_history.js 2>/dev/null || true
node experiment/creative_cycle.js || true
node ci/assert_interop.js || true
node memory_crystals/prune.js --keep=16 2>/dev/null || true
node reports/index.js 2>/dev/null || true
node metrics_export/status.js 2>/dev/null || true
echo "Weekly automation complete."
