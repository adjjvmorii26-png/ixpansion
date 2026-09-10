#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
echo "Running Nexus interop CI…"
node ci/assert_interop.js
