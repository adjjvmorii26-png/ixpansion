#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
LEDGER = REPO / "lab" / "unique_path" / "proof_ledger.jsonl"
PALETTE = [("void", "#05050c"), ("cyan", "#00e5ff"), ("magenta", "#ff2bd6"), ("dim", "#3a3a55"), ("ember", "#ff6b35"), ("ice", "#a8d8ff")]
def main():
    tail, n = "", 0
    if LEDGER.exists():
        lines = LEDGER.read_text().strip().splitlines()[-32:]
        tail, n = "\n".join(lines), len(lines)
    h = hashlib.sha256(tail.encode() or b"empty").hexdigest()
    idx = int(h[:2], 16) % len(PALETTE)
    name, hexc = PALETTE[idx]
    secondary = PALETTE[(idx + 3) % len(PALETTE)]
    print(json.dumps({"ok": True, "project": "merkle_mood", "ledger_tail": n, "mood": name, "primary": hexc, "secondary": secondary[1], "fingerprint": h[:16], "caption": f"mood {name} · ledger×{n}", "ts": datetime.now(timezone.utc).isoformat()}, indent=2))
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
