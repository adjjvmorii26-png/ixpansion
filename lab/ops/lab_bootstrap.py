#!/usr/bin/env python3
"""Lab bootstrap — evolve entrypoint."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
def run(args):
    r = subprocess.run([sys.executable, *args], capture_output=True, text=True, timeout=45)
    try: return r.returncode == 0, json.loads(r.stdout or "{}")
    except json.JSONDecodeError: return r.returncode == 0, {"ok": r.returncode == 0}
def main():
    steps, ok = [], True
    jobs = [
        ("doctrine_diff", [str(REPO / "lab" / "projects" / "doctrine_diff.py")]),
        ("smoke", [str(REPO / "lab" / "smoke_lab.py")]),
        ("constellation", [str(REPO / "lab" / "ops" / "lab_constellation.py")]),
        ("echo", [str(REPO / "lab" / "ops" / "echo_archive.py")]),
        ("soft_gate", [str(REPO / "lab" / "ops" / "soft_gate_report.py")]),
        ("pulse", [str(REPO / "lab" / "ops" / "caption_pulse.py")]),
    ]
    for name, args in jobs:
        if not Path(args[0]).exists():
            steps.append({"step": name, "ok": False, "err": "missing"}); ok = False; continue
        good, _ = run(args)
        steps.append({"step": name, "ok": good}); ok &= good
    out = {"ok": ok, "bootstrap": "lab_v2_evolve", "passed": sum(1 for s in steps if s["ok"]), "n": len(steps), "steps": steps, "ts": datetime.now(timezone.utc).isoformat()}
    (REPO / "docs").mkdir(exist_ok=True)
    (REPO / "docs" / "LAB_BOOTSTRAP.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2)); return 0 if ok else 1
if __name__ == "__main__":
    raise SystemExit(main())
