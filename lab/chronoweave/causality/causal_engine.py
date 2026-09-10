#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
def graph() -> dict:
    g = json.loads((HERE / "causal_graph.csg").read_text()) if (HERE / "causal_graph.csg").exists() else {"nodes": [], "edges": []}
    return {"nodes": g.get("nodes"), "edges": g.get("edges"), "ok": bool(g.get("nodes"))}
if __name__ == "__main__":
    print(json.dumps(graph(), indent=2))
