#!/usr/bin/env python3
import json
from pathlib import Path
STATE = Path(__file__).resolve().parent / "forest.json"
def prune(keep: int = 16) -> dict:
    st = json.loads(STATE.read_text()) if STATE.exists() else {"nodes": []}
    before = len(st["nodes"])
    st["nodes"] = st["nodes"][-keep:]
    STATE.write_text(json.dumps(st, indent=2) + "\n")
    return {"before": before, "after": len(st["nodes"])}
if __name__ == "__main__":
    print(json.dumps(prune()))
