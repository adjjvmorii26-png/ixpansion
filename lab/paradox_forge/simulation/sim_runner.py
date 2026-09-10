#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
def run(name: str = "superpose") -> dict:
    path = HERE / "scenarios" / f"scenario_{name}.sim"
    if not path.exists():
        return {"ok": False, "err": f"missing {name}"}
    sc = json.loads(path.read_text())
    tension = {"break": 0.8, "merge": 0.3, "superpose": 0.55}.get(name, 0.5)
    return {"ok": True, "scenario": sc, "tension": tension}
if __name__ == "__main__":
    print(json.dumps(run(sys.argv[1] if len(sys.argv) > 1 else "superpose"), indent=2))
