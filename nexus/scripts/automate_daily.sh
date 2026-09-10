#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
echo "NEXUS DAILY AUTOMATION  $(date -u +%Y-%m-%dT%H:%M:%SZ)"
node memory_crystals/seed_history.js 2>/dev/null || true
node cli/health.js || true
node orchestrator/quiet.js || true
node reports/index.js 2>/dev/null || true
node metrics_export/status.js 2>/dev/null || true
echo "Daily automation complete."
