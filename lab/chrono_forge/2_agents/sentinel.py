#!/usr/bin/env python3
"""Guards invariants — entropy floor, proof ledger exists, folders ok."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

def check() -> dict:
    issues = []
    sb = ROOT / "sandbox" / "sandbox_state.json"
    if sb.exists():
        st = json.loads(sb.read_text())
        if float(st.get("entropy_budget") or 1) < 0.05:
            issues.append("entropy_floor_breach")
    else:
        issues.append("sandbox_state_missing")
    ledger = ROOT / "lab" / "unique_path" / "proof_ledger.jsonl"
    if not ledger.exists():
        issues.append("proof_ledger_missing")
    return {"agent": "sentinel", "ok": not issues, "issues": issues}

if __name__ == "__main__":
    print(json.dumps(check(), indent=2))
