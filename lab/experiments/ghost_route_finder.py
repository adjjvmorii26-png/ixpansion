#!/usr/bin/env python3
"""Ghost Route Finder — api/wave* without paired test_wave*."""
from __future__ import annotations
import json, re
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
def main():
    api, tests = REPO / "api", REPO / "tests"
    waves, ghosts = [], []
    if api.exists():
        for p in api.glob("wave*.py"):
            m = re.search(r"wave(\d+)", p.name)
            if m: waves.append((m.group(1), p.name))
    for num, name in waves:
        if not tests.exists() or not list(tests.glob(f"test_wave{num}*.py")):
            ghosts.append(name)
    frames = [{"t": "0.0s", "role": "hook", "text": "GHOST ROUTES", "style": "void_cyan"}, {"t": "2.0s", "role": "core", "text": f"{len(ghosts)} unpaired", "style": "magenta"}, {"t": "5.0s", "role": "live", "text": (ghosts[0] if ghosts else "none")[:40], "style": "cyan"}, {"t": "8.0s", "role": "cta", "text": "@CoodingLooop · name the missing tests", "style": "dim"}]
    print(json.dumps({"ok": True, "project": "ghost_route_finder", "wave_n": len(waves), "ghosts": ghosts[:20], "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
