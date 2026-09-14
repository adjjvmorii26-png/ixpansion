#!/usr/bin/env python3
"""Orbit Count — count lab/**/*.py."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
def main():
    lab = REPO / "lab"
    n = len(list(lab.rglob("*.py"))) if lab.exists() else 0
    frames = [{"t":"0.0s","role":"hook","text":"ORBIT COUNT","style":"void_cyan"},{"t":"2.0s","role":"core","text":f"{n} py orbits","style":"magenta"},{"t":"5.0s","role":"live","text":"lab tree","style":"cyan"},{"t":"8.0s","role":"cta","text":"@CoodingLooop · count without vanity","style":"dim"}]
    print(json.dumps({"ok": True, "project": "orbit_count", "n": n, "frames": frames, "audio": None, "ts": datetime.now(timezone.utc).isoformat()}, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
