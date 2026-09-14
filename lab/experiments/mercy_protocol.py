#!/usr/bin/env python3
"""Mercy Protocol — refuse tasks matching planted refusals."""
from __future__ import annotations
import json, re
from datetime import datetime, timezone
REFUSAL_PATTERNS = [r"delete\s+ci", r"silent\s+epoch", r"stock\s+audio", r"token\s*hype", r"force\s+merge\s+stale"]
def decide(task: str) -> dict:
    t = (task or "").lower()
    for pat in REFUSAL_PATTERNS:
        if re.search(pat, t):
            return {"allow": False, "reason": f"matched refusal /{pat}/", "mercy": True}
    return {"allow": True, "reason": "no refusal matched", "mercy": False}
def main():
    import sys
    task = " ".join(sys.argv[1:]) or "run survey on cartography"
    d = decide(task)
    frames = [{"t": "0.0s", "role": "hook", "text": "MERCY PROTOCOL", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": "ALLOW" if d["allow"] else "REFUSE", "style": "magenta"}, {"t": "5.0s", "role": "live", "text": d["reason"][:42], "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · refusal is care", "style": "dim"}]
    print(json.dumps({"ok": True, "project": "mercy_protocol", "task": task, **d, "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
