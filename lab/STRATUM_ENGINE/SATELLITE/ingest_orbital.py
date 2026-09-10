#!/usr/bin/env python3
from __future__ import annotations
import json
from datetime import datetime, timezone
def ingest(raw):
    alt = float(raw.get("alt_km", 400))
    issues = []
    if alt < 150 or alt > 40000: issues.append("alt_out_of_range")
    rec = {"ts": raw.get("ts") or datetime.now(timezone.utc).isoformat(), "source": raw.get("sat_id") or "sat", "lat": float(raw.get("lat", 0)), "lon": float(raw.get("lon", 0)), "alt_km": alt, "value": float(raw.get("value", 0)), "ethics_ok": bool(raw.get("ethics_ok", True)), "domain": "orbital"}
    return {"ok": not issues, "issues": issues, "record": rec}
if __name__ == "__main__":
    print(json.dumps(ingest({"sat_id": "SAT-1", "lat": 0, "lon": 0, "alt_km": 550, "value": 1.02}), indent=2))
