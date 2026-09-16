#!/bin/bash
# IXpansion Codespace Setup — runs on container creation
set -e

echo "🧬 IXpansion Codespace Setup"
echo "============================"

# Python deps
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt -q 2>/dev/null
pip install pyvis graphviz httpx pyyaml -q 2>/dev/null

# Create sandbox dirs
echo "📁 Creating sandbox directories..."
mkdir -p data/sandbox data/sandbox_state data/sandbox_logs output/sandbox

# Verify sandbox keys
echo "🔑 Checking sandbox keys..."
if [ -f .env.sandbox ]; then
    python3 scripts/load_sandbox.py --check
else
    echo "⚠️  No .env.sandbox found — copy from .env.sandbox.example"
fi

# Run velocity check
echo "🚀 Organism velocity check..."
python3 lab/ops/velocity_burst.py 2>/dev/null | head -12 || echo "(velocity check skipped)"

echo ""
echo "✅ Codespace ready!"
echo ""
echo "Quick start:"
echo "  python3 lab/ops/velocity_burst.py    # organism health"
echo "  python3 -m pytest tests/ -q --tb=no  # run tests"
echo "  python3 scripts/load_sandbox.py --check  # verify keys"
echo ""
