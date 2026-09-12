#!/usr/bin/env python3
"""Absence Choir — missing portals as silent voices."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
def main():
    voids = []
    null_script = REPO / "lab" / "null_orchard" / "map_absence.py"
    if null_script.exists():
        r = subprocess.run([sys.executable, str(null_script)], capture_output=True, text=True, timeout=30)
        try: voids = json.loads(r.stdout or "{}").get("voids") or []
        except json.JSONDecodeError: pass
    voices = [v.get("name", "?") for v in voids] or ["openclaw", "wasm_lattice"]
    score = " · ".join(f"∅{n}" for n in voices)
    frames = [{"t":"0.0s","role":"hook","text":"ABSENCE CHOIR","style":"void_cyan"},{"t":"2.0s","role":"core","text":score[:48],"style":"magenta"},{"t":"5.0s","role":"live","text":f"{len(voices)} voices · none filled","style":"cyan"},{"t":"8.0s","role":"cta","text":"@CoodingLooop · the choir is the gap","style":"dim"}]
    out = {"ok": True, "project": "absence_choir", "voices": voices, "n": len(voices), "frames": frames, "audio": None, "doctrine": "the choir is the gap", "ts": datetime.now(timezone.utc).isoformat()}
    dest = REPO / "content_output" / "captions"; dest.mkdir(parents=True, exist_ok=True)
    path = dest / f"choir_{datetime.now(timezone.utc).strftime('%H%M%S')}.json"
    path.write_text(json.dumps({"ok": True, "frames": frames, "audio": None}, indent=2) + "\n"); out["wrote"] = str(path)
    print(json.dumps(out, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
