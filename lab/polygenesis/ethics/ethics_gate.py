#!/usr/bin/env python3
"""Ethics gate — must pass before mutation-like acts."""
from __future__ import annotations
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
def check() -> dict:
    issues = []
    rules = HERE / "ethics_constraints.rule"
    if not rules.exists():
        issues.append("ethics_constraints_missing")
    ledger = ROOT / "lab" / "unique_path" / "proof_ledger.jsonl"
    if not ledger.exists():
        issues.append("proof_ledger_missing")
    text = rules.read_text() if rules.exists() else ""
    if "no_erase_proof_ledger" not in text:
        issues.append("ledger_protection_unspecified")
    return {"ok": not issues, "issues": issues, "mandatory": True}
if __name__ == "__main__":
    print(json.dumps(check(), indent=2))
