#!/usr/bin/env python3
"""Pulse Echo — sandbox entropy reshapes caption intensity curves."""
from __future__ import annotations
import json, math, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
def entropy():
    eng = REPO / "sandbox" / "sandbox_engine.py"
    if eng.exists():
        r = subprocess.run([sys.executable, str(eng), "--status"], capture_output=True, text=True)
        for tok in (r.stdout or "").replace(",", " ").split():
            try:
                v = float(tok)
                if 0 <= v <= 1.5: return v
            except ValueError: pass
    return 0.92
def curve(e, n=8):
    out = []
    for i in range(n):
        t = i / max(n - 1, 1)
        w = 0.3 + 0.7 * abs(math.sin(math.pi * t * (1 + e)))
        out.append({"i": i, "weight": round(w, 3), "glyph": "·✦✧★"[min(3, int(w * 4))]})
    return out
def main():
    e = entropy()
    pack = {"ok": True, "project": "pulse_echo", "entropy": round(e, 4), "curve": curve(e), "caption_hint": f"entropy {e:.2f} shapes the silence", "channel": "@CoodingLooop", "ts": datetime.now(timezone.utc).isoformat()}
    dest = REPO / "content_output" / "echo"; dest.mkdir(parents=True, exist_ok=True)
    p = dest / f"echo_{datetime.now(timezone.utc).strftime('%H%M%S')}.json"
    p.write_text(json.dumps(pack, indent=2) + "\n"); pack["wrote"] = str(p)
    print(json.dumps(pack, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
