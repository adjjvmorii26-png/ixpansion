#!/usr/bin/env python3
"""Caption Pulse — doctrine + tide + scar → channel pulse."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
def jrun(path):
    r = subprocess.run([sys.executable, str(path)], capture_output=True, text=True, timeout=40)
    try: return json.loads(r.stdout or "{}")
    except json.JSONDecodeError: return {}
def main():
    dd, tide, scar = jrun(REPO / "lab" / "projects" / "doctrine_diff.py"), jrun(REPO / "lab" / "ops" / "proof_tide.py"), jrun(REPO / "lab" / "ops" / "route_scar.py")
    cov = dd.get("coverage", 0)
    frames = [{"t": "0.0s", "role": "hook", "text": "LAB PULSE", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": f"doctrine {float(cov):.0%}", "style": "magenta"}, {"t": "4.5s", "role": "live", "text": f"tide {tide.get('phase', '?')} · scar {scar.get('heal_ratio', '?')}", "style": "cyan"}, {"t": "7.5s", "role": "cta", "text": "@CoodingLooop · evolve quietly", "style": "dim"}]
    out = {"ok": True, "project": "caption_pulse", "coverage": cov, "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}
    dest = REPO / "content_output" / "captions"; dest.mkdir(parents=True, exist_ok=True)
    path = dest / f"pulse_{datetime.now(timezone.utc).strftime('%H%M%S')}.json"
    path.write_text(json.dumps({"ok": True, "frames": frames, "audio": None}, indent=2) + "\n"); out["wrote"] = str(path)
    print(json.dumps(out, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
