#!/usr/bin/env python3
"""CF Bridge — call CHRONOFORGE portal from lab ops (main-based)."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
PORTAL = REPO / "lab" / "CHRONOFORGE" / "runtime" / "cf_portal.py"
def main():
    act = sys.argv[1] if len(sys.argv) > 1 else "ethics"
    if not PORTAL.exists():
        print(json.dumps({"ok": False, "err": "cf_portal_missing"})); return 1
    r = subprocess.run([sys.executable, str(PORTAL), act] + sys.argv[2:], capture_output=True, text=True, timeout=60)
    print(r.stdout or r.stderr)
    return r.returncode
if __name__ == "__main__":
    raise SystemExit(main())
