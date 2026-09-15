#!/usr/bin/env python3
"""Fast Board — run quick idea scripts."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
HERE = Path(__file__).resolve().parent
BOARD = ["sigil_clock.py","entropy_meter.py","wave_census.py","caption_splice.py","hex_bundle.py"]
def main():
    res = []
    for s in BOARD:
        p = HERE/s
        if not p.exists(): res.append({"m":s,"ok":False}); continue
        r = subprocess.run([sys.executable,str(p)],capture_output=True,text=True,timeout=35)
        res.append({"m":s,"ok":r.returncode==0})
    ok = all(x["ok"] for x in res)
    print(json.dumps({"ok":ok,"project":"fast_board","passed":sum(1 for x in res if x["ok"]),"n":len(res),"results":res,"ts":datetime.now(timezone.utc).isoformat()},indent=2))
    return 0 if ok else 1
if __name__ == "__main__":
    raise SystemExit(main())
