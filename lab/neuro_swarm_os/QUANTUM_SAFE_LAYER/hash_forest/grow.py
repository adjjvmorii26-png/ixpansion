#!/usr/bin/env python3
import hashlib, json
from pathlib import Path
STATE = Path(__file__).resolve().parent / "forest.json"
def grow(label: str = "leaf") -> dict:
    st = json.loads(STATE.read_text()) if STATE.exists() else {"nodes": []}
    h = hashlib.sha256(f"{label}-{len(st['nodes'])}".encode()).hexdigest()[:16]
    st["nodes"].append({"label": label, "hash": h})
    st["nodes"] = st["nodes"][-64:]
    STATE.write_text(json.dumps(st, indent=2) + "\n")
    return {"grew": h, "n": len(st["nodes"])}
if __name__ == "__main__":
    import sys
    print(json.dumps(grow(sys.argv[1] if len(sys.argv) > 1 else "leaf")))
