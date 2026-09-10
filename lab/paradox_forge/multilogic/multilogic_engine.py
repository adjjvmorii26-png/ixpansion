#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
def status() -> dict:
    states = json.loads((HERE / "logic_states.mlg").read_text()) if (HERE / "logic_states.mlg").exists() else {}
    trans = json.loads((HERE / "logic_transitions.map").read_text()) if (HERE / "logic_transitions.map").exists() else {}
    return {"states": states.get("states"), "transitions": trans, "ok": bool(states.get("states"))}
if __name__ == "__main__":
    print(json.dumps(status(), indent=2))
