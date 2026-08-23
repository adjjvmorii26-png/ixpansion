#!/usr/bin/env python3
"""Meta log of which agent ran (append-only)."""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path

LOG = Path(__file__).resolve().parent / "observer.jsonl"

def note(agent: str, event: str = "ran") -> dict:
    rec = {"ts": datetime.now(timezone.utc).isoformat(), "agent": agent, "event": event}
    with LOG.open("a") as f:
        f.write(json.dumps(rec) + "\n")
    return rec

if __name__ == "__main__":
    print(json.dumps(note(sys.argv[1] if len(sys.argv) > 1 else "unknown"), indent=2))
