"""Health check endpoint for Vercel serverless."""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def handler(request, response):
    """GET /health — system health check."""
    lab_dir = ROOT / "lab" / "experiments"
    module_count = len(list(lab_dir.glob("*.py"))) if lab_dir.exists() else 0

    test_dir = ROOT / "lab" / "tests"
    test_files = list(test_dir.glob("test_*.py")) if test_dir.exists() else []

    return {
        "status": "healthy",
        "version": "0.5.0",
        "modules": module_count,
        "test_suites": len(test_files),
        "mode": os.environ.get("NEXUS_MODE", "development"),
        "seed": int(os.environ.get("NEXUS_SEED", "42")),
    }


if __name__ == "__main__":
    result = handler(None, None)
    print(json.dumps(result, indent=2))
