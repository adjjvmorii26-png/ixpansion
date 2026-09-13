#!/usr/bin/env python3
"""Route Scar — vercel 754→89 as caption memory."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
SCAR = {"event": "vercel_route_collapse", "before": 754, "after": 89, "wave": 409}
def main():
    r = round(1.0 - 89/754, 4)
    frames = [{"t":"0.0s","role":"hook","text":"ROUTE SCAR","style":"void_cyan"},{"t":"2.0s","role":"core","text":"754 → 89 routes","style":"magenta"},{"t":"5.0s","role":"live","text":f"healed {r*100:.1f}% · wave 409","style":"cyan"},{"t":"8.0s","role":"cta","text":"@CoodingLooop · less map, more organism","style":"dim"}]
    out = {"ok": True, "project": "route_scar", "scar": SCAR, "heal_ratio": r, "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}
    dest = Path(__file__).resolve().parents[2] / "content_output" / "captions"; dest.mkdir(parents=True, exist_ok=True)
    path = dest / f"route_scar_{datetime.now(timezone.utc).strftime('%H%M%S')}.json"
    path.write_text(json.dumps({"ok": True, "frames": frames, "audio": None}, indent=2)+"\n"); out["wrote"] = str(path)
    print(json.dumps(out, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
