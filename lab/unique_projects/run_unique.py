#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
LAB = Path(__file__).resolve().parents[1]
JOBS = [
    ("sonify", LAB / "proof_sonifier" / "sonify.py"),
    ("captions", LAB / "caption_lattice" / "weave.py"),
    ("mirror", LAB / "mirror_ledger" / "reflect.py"),
]
def main() -> int:
    results, ok = [], True
    for name, script in JOBS:
        args = [sys.executable, str(script)]
        if name == "mirror": args.append("unique_projects_batch")
        if name == "captions": args += ["--theme", "stratum"]
        r = subprocess.run(args, capture_output=True, text=True, timeout=60)
        results.append({"name": name, "ok": r.returncode == 0})
        ok &= r.returncode == 0
    print(json.dumps({"ok": ok, "projects": results}, indent=2))
    return 0 if ok else 1
if __name__ == "__main__":
    raise SystemExit(main())
