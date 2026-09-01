#!/usr/bin/env python3
import json
from pathlib import Path
MAP = Path(__file__).resolve().parents[1] / "mesh_map.json"
def connect(node_id: str = "edge-1") -> dict:
    m = json.loads(MAP.read_text())
    if not any(n["id"] == node_id for n in m["nodes"]):
        m["nodes"].append({"id": node_id, "role": "edge"})
        m["edges"].append({"from": "local", "to": node_id})
        MAP.write_text(json.dumps(m, indent=2) + "\n")
    return {"connected": node_id, "n": len(m["nodes"])}
if __name__ == "__main__":
    import sys
    print(json.dumps(connect(sys.argv[1] if len(sys.argv) > 1 else "edge-1")))
