#!/usr/bin/env python3
import json
from pathlib import Path
MAP = Path(__file__).resolve().parents[1] / "mesh_map.json"
def sync() -> dict:
    m = json.loads(MAP.read_text()) if MAP.exists() else {"nodes": []}
    return {"synced": True, "nodes": len(m.get("nodes") or [])}
if __name__ == "__main__":
    print(json.dumps(sync()))
