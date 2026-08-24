#!/usr/bin/env python3
"""Score proof ledger density — growth metric, not vanity views."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import json
from collections import Counter
from pathlib import Path

from lab.runtime_vault import ledger_path, read_jsonl, report_path, write_json

LEDGER = ledger_path()
OUT = report_path("proof-density.json")

def measure() -> dict:
    records = read_jsonl(LEDGER)
    if not records:
        return {"ok": True, "lines": 0, "density": 0.0, "cold_start": True}
    types = Counter(str(record.get("type") or "unknown") for record in records)
    lines = [str(record) for record in records]
    n = max(len(lines), 1)
    density = round(len(types) / (n ** 0.5), 4)
    out = {"ok": True, "lines": n, "unique_types": len(types),
           "types": dict(types.most_common(12)), "density": density}
    write_json(OUT, out)
    return out

if __name__ == "__main__":
    print(json.dumps(measure(), indent=2))
