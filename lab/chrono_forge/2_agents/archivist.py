#!/usr/bin/env python3
"""Archivist — summarize last proof ledger lines into lore chronicle."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[3]
LEDGER = ROOT / "lab" / "unique_path" / "proof_ledger.jsonl"
OUT = Path(__file__).resolve().parents[1] / "7_lore" / "chronicles" / "archivist_digest.md"

def digest(n: int = 30) -> dict:
    types = Counter()
    if LEDGER.exists():
        for line in LEDGER.read_text().strip().splitlines()[-n:]:
            try:
                o = json.loads(line)
                types[str(o.get("type") or "unknown")] += 1
            except Exception:
                pass
    body = ["# Archivist digest", "", f"Updated: {datetime.now(timezone.utc).isoformat()}", f"Window: last {n} proof lines", "", "## Type counts"]
    for k, v in types.most_common():
        body.append(f"- `{k}`: {v}")
    body += ["", "The archivist does not sell the past. It counts what was proven."]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(body) + "\n")
    return {"agent": "archivist", "types": dict(types), "path": str(OUT)}

if __name__ == "__main__":
    print(json.dumps(digest(), indent=2))
