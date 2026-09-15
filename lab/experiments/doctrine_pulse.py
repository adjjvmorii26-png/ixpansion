#!/usr/bin/env python3
"""Doctrine Pulse — day-rotated doctrine line for silent captions."""
from __future__ import annotations
import json, hashlib
from datetime import datetime, timezone
LINES = ["additive over rewrite", "lab smoke is not full ci", "chronoforge outlives binaries", "refusal is architecture", "promote by file not branch", "rights before runtime", "only the new surface"]
def main():
    day = datetime.now(timezone.utc).timetuple().tm_yday
    line = LINES[day % len(LINES)]
    h = hashlib.sha256(line.encode()).hexdigest()[:8]
    frames = [{"t": "0.0s", "role": "hook", "text": "DOCTRINE PULSE", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": line, "style": "magenta"}, {"t": "5.0s", "role": "live", "text": f"sig {h}", "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · hold the line", "style": "dim"}]
    print(json.dumps({"ok": True, "project": "doctrine_pulse", "line": line, "sig": h, "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
