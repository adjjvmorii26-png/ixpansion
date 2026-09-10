#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
def run(name: str = "branch") -> dict:
    path = HERE / "scenarios" / f"scenario_{name}.sim"
    if not path.exists():
        return {"ok": False, "err": f"missing {name}"}
    sc = json.loads(path.read_text())
    delta = {"branch": 0.0, "collapse": -0.05, "intervention": -0.02}.get(name, 0.0)
    return {"ok": True, "scenario": sc, "stability_delta": delta}
if __name__ == "__main__":
    print(json.dumps(run(sys.argv[1] if len(sys.argv) > 1 else "branch"), indent=2))
