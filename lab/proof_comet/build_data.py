#!/usr/bin/env python3
from __future__ import annotations
import json, re, hashlib, math
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
LEDGER = REPO / "lab" / "unique_path" / "proof_ledger.jsonl"
INV = REPO / "lab" / "CHRONOFORGE" / "000_ROOT_SPEC" / "invariants.hex"
OUT = Path(__file__).resolve().parent / "data.json"
def main():
    events = []
    if LEDGER.exists():
        for ln in LEDGER.read_text().strip().splitlines()[-40:]:
            try:
                o = json.loads(ln)
                events.append({"type": o.get("type") or o.get("event") or "x", "ts": o.get("ts", "")})
            except json.JSONDecodeError: pass
    root = "0"
    if INV.exists():
        m = re.search(r"INVARIANT_SET_ROOT\s+0x([0-9A-Fa-f]+)", INV.read_text())
        if m: root = m.group(1)[:16]
    h = hashlib.sha256(root.encode()).digest()
    path = []
    for i in range(24):
        ang = (i/24)*6.2832 + (h[i%len(h)]/255)*0.5
        r = 0.3 + 0.5*(i/24)
        path.append({"x": round(math.cos(ang)*r,4), "y": round(math.sin(ang)*r,4), "e": i < len(events)})
    data = {"title": "PROOF COMET", "root": root, "n_events": len(events), "path": path, "events": events[-12:], "channel": "@CoodingLooop", "ts": datetime.now(timezone.utc).isoformat()}
    OUT.write_text(json.dumps(data, indent=2)+"\n")
    print(json.dumps({"ok": True, "wrote": str(OUT), "n_events": len(events), "root": root}, indent=2))
if __name__ == "__main__":
    main()
