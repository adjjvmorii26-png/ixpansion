#!/usr/bin/env python3
"""Phase B: ticket → graft → seams → captions."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
def run(args):
    r = subprocess.run([sys.executable, *args], capture_output=True, text=True, timeout=90)
    return r.returncode == 0
def main():
    steps, ok = [], True
    for name, args in [
        ("ticket", [str(REPO / "lab" / "ops" / "epoch_ticket.py"), "issue", "--ttl", "3600"]),
        ("graft", [str(REPO / "lab" / "ops" / "pr_graft_advisor.py")]),
        ("seams", [str(REPO / "apps" / "seamwalk" / "build_seams.py")]),
        ("captions", [str(REPO / "apps" / "seamwalk" / "to_captions.py")]),
    ]:
        good = run(args)
        steps.append({"step": name, "ok": good}); ok &= good
    print(json.dumps({"ok": ok, "pipeline": "phase_b", "steps": steps}, indent=2))
    return 0 if ok else 1
if __name__ == "__main__":
    raise SystemExit(main())
