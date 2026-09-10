#!/usr/bin/env bash
# Polychron Atlas boot sequence

set -e
cd "$(dirname "$0")"

echo "══════════════════════════════════════════"
echo "  POLYCHRON ATLAS — maps unfolding"
echo "══════════════════════════════════════════"

node glyphstream/glyphstream_flow.js
