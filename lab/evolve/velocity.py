#!/usr/bin/env python3
"""Velocity — critical path for fast lab iteration."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
CRITICAL = [("doctrine", REPO / "lab" / "projects" / "doctrine_diff.py"), ("smoke", REPO / "lab" / "smoke_lab.py"), ("pulse", REPO / "lab" / "ops" / "caption_pulse.py"), ("era", REPO / "lab" / "evolve" / "era_pack.py")]
def main():
    steps, ok = [], True
    for name, path in CRITICAL:
        if not path.exists():
            steps.append({"name": name, "ok": False, "err": "missing"}); ok = False; continue
        r = subprocess.run([sys.executable, str(path)], capture_output=True, text=True, timeout=50)
        steps.append({"name": name, "ok": r.returncode == 0}); ok &= r.returncode == 0
    out = {"ok": ok, "velocity": "critical_path", "passed": sum(1 for s in steps if s["ok"]), "n": len(steps), "steps": steps, "ts": datetime.now(timezone.utc).isoformat()}
    print(json.dumps(out, indent=2)); return 0 if ok else 1
if __name__ == "__main__":
    raise SystemExit(main())
