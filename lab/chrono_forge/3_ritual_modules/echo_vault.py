#!/usr/bin/env python3
"""Store temporal anomalies when delta paradox conditions appear."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import json
from datetime import datetime, timezone
from pathlib import Path

from lab.runtime_vault import append_jsonl, ledger_path

VAULT = ledger_path("echo-anomalies.jsonl")

def record(kind: str, detail: dict) -> dict:
    rec = {"ts": datetime.now(timezone.utc).isoformat(), "kind": kind, "detail": detail}
    append_jsonl(VAULT, rec)
    return rec

if __name__ == "__main__":
    print(json.dumps(record("manual_probe", {"note": "echo vault online"}), indent=2))
