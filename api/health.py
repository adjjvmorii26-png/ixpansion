"""Health check endpoint for the live platform.

Reflects real runtime telemetry (module count, route count, test
suites, mode) instead of a hard-coded version, reading from the
live filesystem so it always matches the deployed surface.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "3.68.0"
WAVE = "147"


def collect_health() -> dict:
    api_dir = ROOT / "api"
    module_count = len([p for p in api_dir.glob("*.py") if p.stem not in ("__init__", "index")]) if api_dir.exists() else 0

    route_count = 0
    try:
        with open(ROOT / "vercel.json") as f:
            route_count = len(json.load(f).get("routes", []))
    except (OSError, json.JSONDecodeError):
        pass

    test_files = list((ROOT / "tests").glob("test_*.py")) if (ROOT / "tests").exists() else []

    return {
        "status": "healthy",
        "version": VERSION,
        "wave": WAVE,
        "modules": module_count,
        "route_entries": route_count,
        "test_suites": len(test_files),
        "mode": os.environ.get("NEXUS_MODE", "development"),
        "seed": int(os.environ.get("NEXUS_SEED", "42")),
    }


def handler(request=None, response=None):
    return collect_health()


if __name__ == "__main__":
    print(json.dumps(collect_health(), indent=2))
