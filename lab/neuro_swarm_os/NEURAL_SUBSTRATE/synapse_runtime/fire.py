#!/usr/bin/env python3
"""Fire a synthetic synapse event."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

STATE = Path(__file__).resolve().parent / "fire_log.jsonl"

def fire(pre: str, post: str, w: float = 0.1) -> dict:
    rec = {"ts": datetime.now(timezone.utc).isoformat(), "pre": pre, "post": post, "w": w}
    with STATE.open("a") as f:
        f.write(json.dumps(rec) + "\n")
    return rec

if __name__ == "__main__":
    print(json.dumps(fire("dendrite", "agent"), indent=2))
