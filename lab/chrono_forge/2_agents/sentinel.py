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

from lab.runtime_vault import ledger_path, state_path


def check() -> dict:
    issues = []
    sb = state_path("sandbox", "engine.json")
    if sb.exists():
        st = json.loads(sb.read_text())
        if float(st.get("entropy_budget") or 1) < 0.05:
            issues.append("entropy_floor_breach")
    ledger = ledger_path()
    return {"agent": "sentinel", "ok": not issues,
            "issues": issues, "ledger": "cold-start" if not ledger.exists() else "present"}

if __name__ == "__main__":
    print(json.dumps(check(), indent=2))
