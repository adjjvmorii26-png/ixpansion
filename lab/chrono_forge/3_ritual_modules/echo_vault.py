#!/usr/bin/env python3
"""Store temporal anomalies when delta paradox conditions appear."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

VAULT = Path(__file__).resolve().parents[1] / "7_lore" / "anomalies" / "echo_vault.jsonl"
VAULT.parent.mkdir(parents=True, exist_ok=True)

def record(kind: str, detail: dict) -> dict:
    rec = {"ts": datetime.now(timezone.utc).isoformat(), "kind": kind, "detail": detail}
    with VAULT.open("a") as f:
        f.write(json.dumps(rec) + "\n")
    return rec

if __name__ == "__main__":
    print(json.dumps(record("manual_probe", {"note": "echo vault online"}), indent=2))
