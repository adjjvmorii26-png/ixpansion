#!/usr/bin/env python3
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
HERE = Path(__file__).resolve().parent
METRICS = HERE / "metrics.json"
def snapshot(extra=None):
    data = {}
    if METRICS.exists():
        try: data = json.loads(METRICS.read_text())
        except json.JSONDecodeError: data = {}
    data["updated"] = datetime.now(timezone.utc).isoformat()
    if extra: data.setdefault("kpi", {}).update(extra)
    METRICS.write_text(json.dumps(data, indent=2) + "\n")
    return {"ok": True, "metrics": data}
if __name__ == "__main__":
    print(json.dumps(snapshot({"stratum_version": "1.1.0-lab", "refinements": 1}), indent=2))
