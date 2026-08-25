#!/usr/bin/env python3
"""Live Experiment Runner — execute experiments with real-time telemetry.

Bridges the lab experiments with the Vercel API by providing a
runner that can execute any experiment module, capture its output,
and return structured telemetry data suitable for dashboard display.

The runner:
1. Imports the experiment module
2. Calls its demo() function
3. Captures timing, memory, and output metrics
4. Returns a structured result with full telemetry
"""
from __future__ import annotations

import hashlib
import importlib
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def run_experiment(name: str, seed: int = 42) -> dict[str, Any]:
    """Run an experiment and capture telemetry."""
    lab_dir = ROOT / "lab" / "experiments"
    module_path = lab_dir / f"{name}.py"

    if not module_path.exists():
        return {"error": f"experiment '{name}' not found", "available": _list_experiments()}

    start_time = time.time()
    start_mono = time.monotonic()

    try:
        spec = importlib.util.spec_from_file_location(
            f"lab.experiments.{name}", str(module_path)
        )
        if not spec or not spec.loader:
            return {"error": f"cannot load module '{name}'"}

        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        if hasattr(mod, "demo"):
            result = mod.demo()
        elif hasattr(mod, "main"):
            result = {"status": "has_main_only"}
        else:
            result = {"status": "no_entry_point"}

        elapsed = time.monotonic() - start_mono

        return {
            "name": name,
            "status": "success",
            "result": result,
            "telemetry": {
                "elapsed_ms": round(elapsed * 1000, 2),
                "timestamp": start_time,
                "result_type": type(result).__name__,
                "result_size": len(json.dumps(result, default=str)),
                "module_path": str(module_path.relative_to(ROOT)),
            },
            "run_id": hashlib.sha256(
                f"{name}:{start_time}".encode()
            ).hexdigest()[:12],
        }
    except Exception as e:
        elapsed = time.monotonic() - start_mono
        return {
            "name": name,
            "status": "error",
            "error": str(e),
            "telemetry": {
                "elapsed_ms": round(elapsed * 1000, 2),
                "timestamp": start_time,
            },
        }


def _list_experiments() -> list[str]:
    lab_dir = ROOT / "lab" / "experiments"
    if not lab_dir.exists():
        return []
    return [f.stem for f in sorted(lab_dir.glob("*.py"))
            if not f.name.startswith("_")]


def run_all(seeds: int = 1) -> dict[str, Any]:
    """Run all experiments and collect summary."""
    experiments = _list_experiments()
    results = []
    total_ms = 0.0

    for name in experiments:
        r = run_experiment(name)
        results.append(r)
        total_ms += r.get("telemetry", {}).get("elapsed_ms", 0)

    successes = sum(1 for r in results if r.get("status") == "success")
    errors = sum(1 for r in results if r.get("status") == "error")

    return {
        "total_experiments": len(experiments),
        "successes": successes,
        "errors": errors,
        "total_time_ms": round(total_ms, 2),
        "avg_time_ms": round(total_ms / max(1, len(experiments)), 2),
        "results": [
            {"name": r["name"], "status": r["status"],
             "ms": r.get("telemetry", {}).get("elapsed_ms", 0)}
            for r in results
        ],
    }


def demo() -> dict[str, Any]:
    return run_all()


def main() -> None:
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
