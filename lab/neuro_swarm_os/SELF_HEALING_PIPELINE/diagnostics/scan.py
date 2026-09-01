#!/usr/bin/env python3
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]
def scan() -> dict:
    issues = []
    for req in ["lab/experiments/lab_smoke.py", "sandbox/sandbox_engine.py", "lab/pinned_projects.json"]:
        if not (ROOT / req).exists():
            issues.append(req)
    return {"ok": not issues, "missing": issues, "root": str(ROOT)}
if __name__ == "__main__":
    print(json.dumps(scan(), indent=2))
