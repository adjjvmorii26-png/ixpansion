#!/usr/bin/env python3
"""Carnival — run experimental shows in one pass."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
HERE = Path(__file__).resolve().parent
SHOWS = ["dream_residue.py","soft_eclipse.py","lattice_haiku.py","ghost_orbit.py","chrono_seed.py","ink_budget.py"]
def main():
    results = []
    for s in SHOWS:
        p = HERE / s
        if not p.exists(): results.append({"show": s, "ok": False}); continue
        r = subprocess.run([sys.executable, str(p)], capture_output=True, text=True, timeout=30)
        results.append({"show": s, "ok": r.returncode == 0})
    ok = all(x["ok"] for x in results)
    frames = [{"t":"0.0s","role":"hook","text":"LAB CARNIVAL","style":"void_cyan"},{"t":"2.0s","role":"core","text":f"{sum(1 for x in results if x['ok'])}/{len(results)} shows","style":"magenta"},{"t":"5.0s","role":"live","text":"residue · eclipse · haiku · ghosts","style":"cyan"},{"t":"8.0s","role":"cta","text":"@CoodingLooop · the lab is awake","style":"dim"}]
    print(json.dumps({"ok":ok,"project":"carnival","results":results,"frames":frames,"audio":None,"ts":datetime.now(timezone.utc).isoformat()},indent=2)); return 0 if ok else 1
if __name__ == "__main__":
    raise SystemExit(main())
