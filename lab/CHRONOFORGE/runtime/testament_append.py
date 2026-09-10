#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path
HERE = Path(__file__).resolve().parent
LOG = HERE.parent / "070_TESTAMENTS" / "E1" / "migration_logs" / "testaments.jsonl"

def append(kind: str, body: dict) -> dict:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {"ts": datetime.now(timezone.utc).isoformat(), "kind": kind, **body}
    with LOG.open("a") as f:
        f.write(json.dumps(entry) + "\n")
    return {"ok": True, "entry": entry}

if __name__ == "__main__":
    print(json.dumps(append(sys.argv[1] if len(sys.argv) > 1 else "note", {"note": sys.argv[2] if len(sys.argv) > 2 else "lab"}), indent=2))
