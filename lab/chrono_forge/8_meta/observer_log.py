#!/usr/bin/env python3
"""Meta log of which agent ran (append-only)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import json, sys
from datetime import datetime, timezone
from pathlib import Path

from lab.runtime_vault import append_jsonl, state_path

LOG = state_path("observer.jsonl")

def note(agent: str, event: str = "ran") -> dict:
    rec = {"ts": datetime.now(timezone.utc).isoformat(), "agent": agent, "event": event}
    append_jsonl(LOG, rec)
    return rec

if __name__ == "__main__":
    print(json.dumps(note(sys.argv[1] if len(sys.argv) > 1 else "unknown"), indent=2))
