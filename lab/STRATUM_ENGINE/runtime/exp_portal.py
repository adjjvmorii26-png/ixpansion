#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
SE = ROOT.parent
EXPS = {
    "fog": SE / "EXPERIMENTS" / "uncertainty_fog.py",
    "glyph-route": SE / "EXPERIMENTS" / "glyph_router.py",
    "ghost-orbit": SE / "EXPERIMENTS" / "ghost_orbit.py",
    "safe-patch": SE / "EXPERIMENTS" / "safe_paradox_patch.py",
}
def main() -> int:
    act = (sys.argv[1] if len(sys.argv) > 1 else "help").lower()
    if act in ("help", "-h", "--help"):
        print(json.dumps({"experiments": list(EXPS), "usage": "python exp_portal.py <exp> [args]"}, indent=2))
        return 0
    if act not in EXPS:
        print(json.dumps({"ok": False, "err": "unknown", "experiments": list(EXPS)}))
        return 1
    r = subprocess.run([sys.executable, str(EXPS[act])] + sys.argv[2:], capture_output=True, text=True)
    print(r.stdout or r.stderr)
    return r.returncode
if __name__ == "__main__":
    raise SystemExit(main())
