#!/usr/bin/env python3
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[5]
def scout() -> dict:
    hits = []
    lab = ROOT / "lab"
    if lab.exists():
        for p in lab.rglob("*.py"):
            hits.append(str(p.relative_to(ROOT))[:60])
            if len(hits) >= 5:
                break
    return {"agent": "scout", "samples": hits, "ok": True}
if __name__ == "__main__":
    print(json.dumps(scout()))
