#!/usr/bin/env python3
"""Ink Budget — scarce caption frames as craft."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
CAP = REPO / "content_output" / "captions"
DAILY = 48
def main():
    used = 0
    if CAP.exists():
        for f in CAP.glob("*.json"):
            try: used += len(json.loads(f.read_text()).get("frames") or [])
            except Exception: pass
    remaining = max(0, DAILY - (used % (DAILY*3)))
    frames = [{"t":"0.0s","role":"hook","text":"INK BUDGET","style":"void_cyan"},{"t":"2.0s","role":"core","text":f"{remaining} frames left (soft)","style":"magenta"},{"t":"5.0s","role":"live","text":f"spent ~{used} lifetime","style":"cyan"},{"t":"8.0s","role":"cta","text":"@CoodingLooop · spend ink wisely","style":"dim"}]
    print(json.dumps({"ok":True,"project":"ink_budget","used":used,"daily_soft":DAILY,"remaining_soft":remaining,"frames":frames,"audio":None,"doctrine":"scarcity is craft","ts":datetime.now(timezone.utc).isoformat()},indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
