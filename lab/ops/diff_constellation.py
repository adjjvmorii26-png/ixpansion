#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, math, sys
from datetime import datetime, timezone
SECTORS = {"lab/": "organism", "sandbox/": "pulse", ".github/": "gate", "docs/": "lore", "content_output/": "signal"}
def sector(path):
    for prefix, name in SECTORS.items():
        if path.startswith(prefix) or f"/{prefix}" in path: return name
    return "outer"
def place(path):
    h = hashlib.sha256(path.encode()).digest()
    ang = (h[0]/255)*2*math.pi; r = 0.25+(h[1]/255)*0.7
    return {"path": path, "sector": sector(path), "x": round(math.cos(ang)*r,4), "y": round(math.sin(ang)*r,4), "mag": round(0.4+(h[2]/255)*0.6,3)}
def main():
    paths = [p for p in sys.argv[1:] if p] or ["lab/ops/pr_graft_advisor.py", ".github/workflows/lab-graft.yml", "sandbox/sandbox_engine.py"]
    nodes = [place(p) for p in paths]
    by = {}
    for n in nodes: by[n["sector"]] = by.get(n["sector"], 0) + 1
    print(json.dumps({"ok": True, "project": "diff_constellation", "n": len(nodes), "sectors": by, "nodes": nodes, "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
