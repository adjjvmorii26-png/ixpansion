#!/usr/bin/env python3
"""Run a named scenario stub."""
from __future__ import annotations
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
def run(name: str = "growth") -> dict:
    path = HERE / "scenarios" / f"scenario_{name}.sim"
    if not path.exists():
        return {"ok": False, "err": f"missing scenario {name}"}
    sc = json.loads(path.read_text())
    return {"ok": True, "scenario": sc, "fitness_delta": 0.01 if name == "growth" else -0.02}
if __name__ == "__main__":
    print(json.dumps(run(sys.argv[1] if len(sys.argv) > 1 else "growth"), indent=2))
