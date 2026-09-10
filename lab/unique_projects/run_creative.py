#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
LAB = Path(__file__).resolve().parents[1]
JOBS = [("comet_data", LAB/"proof_comet"/"build_data.py", []), ("entropy_cap", LAB/"entropy_caption"/"bridge.py", []), ("stamp", LAB/"sigil_stamp"/"stamp.py", ["proof_comet"])]
def main():
    results, ok = [], True
    for name, script, args in JOBS:
        r = subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True, timeout=60)
        results.append({"name": name, "ok": r.returncode == 0}); ok &= r.returncode == 0
    print(json.dumps({"ok": ok, "creative": results}, indent=2))
    return 0 if ok else 1
if __name__ == "__main__":
    raise SystemExit(main())
