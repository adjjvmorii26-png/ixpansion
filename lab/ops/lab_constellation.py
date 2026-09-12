#!/usr/bin/env python3
"""Lab Constellation — scar + silence + tide → one caption pack."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
OPS = REPO / "lab" / "ops"
def jrun(script):
    r = subprocess.run([sys.executable, str(OPS / script)], capture_output=True, text=True, timeout=60)
    try: return json.loads(r.stdout or "{}")
    except json.JSONDecodeError: return {"ok": r.returncode == 0}
def main():
    scar, silence, tide = jrun("route_scar.py"), jrun("silence_ledger.py"), jrun("proof_tide.py")
    frames = [
        {"t": "0.0s", "role": "hook", "text": "LAB CONSTELLATION", "style": "void_cyan"},
        {"t": "2.0s", "role": "core", "text": f"scar heal {scar.get('heal_ratio', '?')}", "style": "magenta"},
        {"t": "4.5s", "role": "live", "text": f"silence capital {silence.get('frame_capital', 0)} frames", "style": "cyan"},
        {"t": "7.0s", "role": "live", "text": f"tide {tide.get('phase')} · {tide.get('level')}", "style": "cyan"},
        {"t": "9.5s", "role": "cta", "text": "@CoodingLooop · constellation over noise", "style": "dim"},
    ]
    out = {"ok": all(x.get("ok") for x in (scar, silence, tide)), "project": "lab_constellation", "scar_heal": scar.get("heal_ratio"), "frame_capital": silence.get("frame_capital"), "tide": {"phase": tide.get("phase"), "level": tide.get("level")}, "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}
    dest = REPO / "content_output" / "captions"; dest.mkdir(parents=True, exist_ok=True)
    path = dest / f"constellation_{datetime.now(timezone.utc).strftime('%H%M%S')}.json"
    path.write_text(json.dumps({"ok": True, "frames": frames, "audio": None}, indent=2) + "\n")
    out["wrote"] = str(path)
    print(json.dumps(out, indent=2)); return 0 if out["ok"] else 1
if __name__ == "__main__":
    raise SystemExit(main())
