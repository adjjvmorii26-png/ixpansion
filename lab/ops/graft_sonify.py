#!/usr/bin/env python3
from __future__ import annotations
import json, hashlib, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
REPORTS = REPO / "lab" / "ops" / "graft_reports"
def latest():
    if not REPORTS.exists(): return {}
    files = sorted(REPORTS.glob("graft_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return json.loads(files[0].read_text()) if files else {}
def sonify(g, beats=8):
    action = g.get("action", "hold"); fused = float(g.get("fused") or 0)
    raw = hashlib.sha256(f"{action}|{fused}|{g.get('ts','')}".encode()).digest()
    alphabet = {"act": "★✦✧·", "observe": "◇◈○·", "hold": "▪▫· "}.get(action, "·")
    grid = [{"beat": i, "intensity": round((raw[i%len(raw)]%16)/15.0*(0.4+0.6*fused), 3), "glyph": alphabet[raw[i%len(raw)]%len(alphabet)], "slot": f"T+{i*0.35:.1f}s"} for i in range(beats)]
    return {"ok": True, "project": "graft_sonify", "action": action, "fused": fused, "beats": grid, "caption": f"graft {action} · fused {fused:.2f}", "channel": "@CoodingLooop", "ts": datetime.now(timezone.utc).isoformat()}
def main():
    g = latest()
    if not g:
        subprocess.run([sys.executable, str(REPO/"lab"/"ops"/"pr_graft_advisor.py")], capture_output=True); g = latest()
    out = sonify(g or {"action": "hold", "fused": 0})
    dest = REPO/"content_output"/"graft_audio_scores"; dest.mkdir(parents=True, exist_ok=True)
    p = dest / f"score_{datetime.now(timezone.utc).strftime('%H%M%S')}.json"; p.write_text(json.dumps(out, indent=2)+"\n"); out["wrote"] = str(p)
    print(json.dumps(out, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
