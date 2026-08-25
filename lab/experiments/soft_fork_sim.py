#!/usr/bin/env python3
"""Soft fork: shadow branch of proof ledger without mutating main."""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "lab" / "unique_path" / "proof_ledger.jsonl"
OUT = Path(__file__).resolve().parent / "soft_fork.json"

def sim(label: str = "shadow-A") -> dict:
    lines = []
    if LEDGER.exists():
        lines = [ln for ln in LEDGER.read_text().strip().splitlines() if ln.strip()]
    tip = lines[-1] if lines else "{}"
    tip_hash = hashlib.sha256(tip.encode()).hexdigest()[:16]
    shadow = {
        "fork": label,
        "parent_tip": tip_hash,
        "parent_len": len(lines),
        "proposed": {"type": "soft_fork_probe", "ref": label,
                     "ts": datetime.now(timezone.utc).isoformat()},
        "merge_policy": "observe_only",
    }
    OUT.write_text(json.dumps(shadow, indent=2) + "\n")
    print(json.dumps(shadow, indent=2))
    return shadow

if __name__ == "__main__":
    import sys
    sim(sys.argv[1] if len(sys.argv) > 1 else "shadow-A")
