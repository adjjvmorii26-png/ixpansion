#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
def check() -> dict:
    issues = []
    rules = HERE / "ethics_temporal.rule"
    if not rules.exists():
        issues.append("ethics_temporal_missing")
    text = rules.read_text() if rules.exists() else ""
    for req in ("no_rewrite_past_without_audit", "no_intervention_without_ethics_gate"):
        if req not in text:
            issues.append(f"missing_{req}")
    ledger = ROOT / "lab" / "unique_path" / "proof_ledger.jsonl"
    if not ledger.exists():
        issues.append("proof_ledger_missing")
    return {"ok": not issues, "issues": issues, "mandatory": True}
if __name__ == "__main__":
    print(json.dumps(check(), indent=2))
