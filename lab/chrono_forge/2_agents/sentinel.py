#!/usr/bin/env python3
"""Guards invariants — entropy floor, proof ledger exists."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import json
from pathlib import Path

from lab.runtime_vault import ledger_path, state_path, verify_jsonl


def check() -> dict:
    issues = []
    sb = state_path("sandbox", "engine.json")
    if sb.exists():
        st = json.loads(sb.read_text())
        if float(st.get("entropy_budget") or 1) < 0.05:
            issues.append("entropy_floor_breach")
    ledger = ledger_path()
    audit = None
    ledger_state = "cold-start"
    if ledger.exists():
        ledger_state = "present"
        audit = verify_jsonl(ledger)
        if not audit["ok"]:
            issues.append("ledger_chain_broken")
    return {"agent": "sentinel", "ok": not issues, "issues": issues,
            "ledger": ledger_state, "ledger_audit": audit}

if __name__ == "__main__":
    print(json.dumps(check(), indent=2))
