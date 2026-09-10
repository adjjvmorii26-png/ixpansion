#!/usr/bin/env python3
from __future__ import annotations
import json, sys
RULES = {"max_value": 1e6, "min_value": -1e6, "require_ethics_tag": True}
def check(payload: dict) -> dict:
    issues = []
    v = payload.get("value")
    if v is not None:
        if v > RULES["max_value"]: issues.append("max_value")
        if v < RULES["min_value"]: issues.append("min_value")
    if RULES["require_ethics_tag"] and not payload.get("ethics_ok", False):
        issues.append("ethics_required")
    return {"ok": not issues, "issues": issues, "rules": RULES}
if __name__ == "__main__":
    demo = {"value": 1.0, "ethics_ok": True}
    if len(sys.argv) > 1 and sys.argv[1] == "fail":
        demo = {"value": 1.0, "ethics_ok": False}
    print(json.dumps(check(demo), indent=2))
