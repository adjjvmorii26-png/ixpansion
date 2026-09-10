#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
LEDGER = REPO / "lab" / "unique_path" / "proof_ledger.jsonl"
INV = REPO / "lab" / "CHRONOFORGE" / "000_ROOT_SPEC" / "invariants.hex"
def ledger_tail(n=20):
    if not LEDGER.exists(): return []
    out = []
    for ln in LEDGER.read_text().strip().splitlines()[-n:]:
        try: out.append(json.loads(ln))
        except json.JSONDecodeError: pass
    return out
def root_nibble():
    if not INV.exists(): return "0"*8
    m = re.search(r"INVARIANT_SET_ROOT\s+0x([0-9A-Fa-f]+)", INV.read_text())
    return (m.group(1) if m else "0"*8)[:8]
def pattern_from_hash(h, beats):
    raw = hashlib.sha256(h.encode()).digest()
    return [{"beat": i, "intensity": round((raw[i%len(raw)]%16)/15.0, 3), "glyph": "░▒▓█"[raw[i%len(raw)]%4], "caption_slot": f"T+{i*0.4:.1f}s"} for i in range(beats)]
def sonify(beats=8):
    tail = ledger_tail(30)
    density = len(tail)/30.0
    root = root_nibble()
    return {"ok": True, "project": "proof_sonifier", "channel": "@CoodingLooop", "mode": "silent_caption_score", "ledger_tail": len(tail), "density": round(density, 3), "invariant_nibbles": root, "beats": pattern_from_hash(f"{root}|{len(tail)}|{density}", beats), "ts": datetime.now(timezone.utc).isoformat()}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--beats", type=int, default=8)
    print(json.dumps(sonify(ap.parse_args().beats), indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
