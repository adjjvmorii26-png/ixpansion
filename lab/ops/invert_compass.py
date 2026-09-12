#!/usr/bin/env python3
"""Invert Compass — point at the smallest honest next step."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
OPS = Path(__file__).resolve().parent
STEPS = ["run smoke_lab once", "deposit one caption frame", "walk one SEAMWALK rift without filling it", "issue one epoch ticket", "read dual_track_card"]
def main():
    graft = {}
    g = OPS / "pr_graft_advisor.py"
    if g.exists():
        r = subprocess.run([sys.executable, str(g)], capture_output=True, text=True, timeout=90)
        try: graft = json.loads(r.stdout or "{}")
        except json.JSONDecodeError: pass
    action = graft.get("action", "observe")
    idx = {"hold": 0, "observe": 1, "act": 2}.get(action, 1)
    step = STEPS[idx % len(STEPS)]
    frames = [{"t":"0.0s","role":"hook","text":"INVERT COMPASS","style":"void_cyan"},{"t":"2.0s","role":"core","text":f"graft was {action}","style":"magenta"},{"t":"5.0s","role":"live","text":step,"style":"cyan"},{"t":"8.0s","role":"cta","text":"@CoodingLooop · smallest next truth","style":"dim"}]
    out = {"ok": True, "project": "invert_compass", "graft_action": action, "next": step, "frames": frames, "audio": None, "doctrine": "point at the smallest next truth", "ts": datetime.now(timezone.utc).isoformat()}
    dest = REPO / "content_output" / "captions"; dest.mkdir(parents=True, exist_ok=True)
    path = dest / f"compass_{datetime.now(timezone.utc).strftime('%H%M%S')}.json"
    path.write_text(json.dumps({"ok": True, "frames": frames, "audio": None}, indent=2) + "\n"); out["wrote"] = str(path)
    print(json.dumps(out, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
