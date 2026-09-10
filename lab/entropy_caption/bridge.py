#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
def sandbox_entropy():
    eng = REPO / "sandbox" / "sandbox_engine.py"
    if not eng.exists(): return None
    r = subprocess.run([sys.executable, str(eng), "--status"], capture_output=True, text=True)
    for tok in (r.stdout or "").replace(",", " ").split():
        try:
            v = float(tok)
            if 0 <= v <= 1.5: return v
        except ValueError: pass
    return None
def caption():
    e = sandbox_entropy()
    if e is None: e = 0.95
    mood = "overclocked void" if e > 1 else "high entropy bloom" if e > 0.7 else "steady lattice" if e > 0.4 else "quiet freeze"
    line = f"entropy {e:.3f} · {mood} · proof > spectacle"
    out = {"ok": True, "project": "entropy_caption", "entropy": e, "caption": line, "channel": "@CoodingLooop", "ts": datetime.now(timezone.utc).isoformat()}
    dest = REPO / "content_output" / "captions"; dest.mkdir(parents=True, exist_ok=True)
    p = dest / f"entropy_{datetime.now(timezone.utc).strftime('%H%M%S')}.json"
    p.write_text(json.dumps(out, indent=2)+"\n"); out["wrote"] = str(p)
    return out
if __name__ == "__main__":
    print(json.dumps(caption(), indent=2))
