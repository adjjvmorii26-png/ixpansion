#!/usr/bin/env python3
"""Prevent infinite descent in form invention / self-rewrite loops."""
from __future__ import annotations
import json
from pathlib import Path

STATE = Path(__file__).resolve().parent / "recursion_state.json"
MAX_DEPTH = 5

def enter(label: str) -> dict:
    st = json.loads(STATE.read_text()) if STATE.exists() else {"depth": 0, "stack": []}
    depth = int(st.get("depth") or 0) + 1
    stack = list(st.get("stack") or []) + [label]
    if depth > MAX_DEPTH:
        return {"ok": False, "reason": "recursion_anchor_trip", "depth": depth, "max": MAX_DEPTH, "stack": stack}
    STATE.write_text(json.dumps({"depth": depth, "stack": stack}, indent=2) + "\n")
    return {"ok": True, "depth": depth, "stack": stack}

def reset() -> dict:
    STATE.write_text(json.dumps({"depth": 0, "stack": []}, indent=2) + "\n")
    return {"ok": True, "depth": 0}

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "reset":
        print(json.dumps(reset(), indent=2))
    else:
        print(json.dumps(enter(sys.argv[1] if len(sys.argv) > 1 else "default"), indent=2))
