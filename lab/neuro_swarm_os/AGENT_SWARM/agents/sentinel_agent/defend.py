#!/usr/bin/env python3
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[5]
def defend() -> dict:
    issues = []
    if not (ROOT / "lab" / "unique_path" / "proof_ledger.jsonl").exists():
        issues.append("proof_ledger_missing")
    return {"agent": "sentinel", "ok": not issues, "issues": issues}
if __name__ == "__main__":
    print(json.dumps(defend()))
