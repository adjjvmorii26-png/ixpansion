#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
COPY = {"act": ("GRAFT GREEN", "organism surfaces aligned", "merge-advice: act"), "observe": ("GRAFT BAND", "uncertainty crosses threshold", "human eye required"), "hold": ("GRAFT HOLD", "signals below threshold", "do not graft yet")}
def main():
    subprocess.run([sys.executable, str(REPO/"lab"/"ops"/"pr_graft_advisor.py")], capture_output=True, timeout=90)
    reports = sorted((REPO/"lab"/"ops"/"graft_reports").glob("graft_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    g = json.loads(reports[0].read_text()) if reports else {"action": "hold", "fused": 0}
    action = g.get("action", "hold"); hook, core, live = COPY.get(action, COPY["hold"])
    frames = [{"t": "0.0s", "role": "hook", "text": hook, "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": core, "style": "magenta"}, {"t": "5.0s", "role": "live", "text": f"{live} · fused {g.get('fused')}", "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · proof > spectacle", "style": "dim"}]
    out = {"ok": True, "project": "graft_caption_reactor", "action": action, "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}
    dest = REPO/"content_output"/"captions"; dest.mkdir(parents=True, exist_ok=True)
    path = dest / f"graft_rx_{action}_{datetime.now(timezone.utc).strftime('%H%M%S')}.json"
    path.write_text(json.dumps(out, indent=2)+"\n"); out["wrote"] = str(path)
    print(json.dumps(out, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
