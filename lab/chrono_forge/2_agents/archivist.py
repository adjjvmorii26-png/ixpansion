#!/usr/bin/env python3
"""Archivist — summarize last proof ledger lines into lore chronicle."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import json
from datetime import datetime, timezone
from pathlib import Path
from collections import Counter

from lab.runtime_vault import ledger_path, read_jsonl, report_path

LEDGER = ledger_path()
OUT = report_path("archivist-digest.md")

def digest(n: int = 30) -> dict:
    types = Counter()
    for record in read_jsonl(LEDGER)[-n:]:
        types[str(record.get("type") or "unknown")] += 1
    body = ["# Archivist digest", "", f"Updated: {datetime.now(timezone.utc).isoformat()}", f"Window: last {n} proof lines", "", "## Type counts"]
    for k, v in types.most_common():
        body.append(f"- `{k}`: {v}")
    body += ["", "The archivist does not sell the past. It counts what was proven."]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(body) + "\n")
    return {"agent": "archivist", "types": dict(types), "path": str(OUT)}

if __name__ == "__main__":
    print(json.dumps(digest(), indent=2))
