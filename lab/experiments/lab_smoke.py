#!/usr/bin/env python3
"""Lab smoke: pulse, sentinel, merkle, recursion anchor — no third-party deps."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CF = ROOT / "lab" / "chrono_forge"
EXP = ROOT / "lab" / "experiments"

def run(cmd: list[str]) -> tuple[bool, str]:
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    return r.returncode == 0, (r.stdout or "")[-300:]

def main() -> int:
    checks = []
    ok_all = True
    for name, cmd in [
        ("pulse", [sys.executable, str(CF / "0_primal_core" / "pulse_driver.py"), "--beats", "1"]),
        ("sentinel", [sys.executable, str(CF / "2_agents" / "sentinel.py")]),
        ("recursion_reset", [sys.executable, str(EXP / "recursion_anchor.py"), "reset"]),
        ("sandbox_status", [sys.executable, str(ROOT / "sandbox" / "sandbox_engine.py"), "--status"]),
    ]:
        o, _ = run(cmd)
        checks.append({"name": name, "ok": o})
        ok_all &= o
    print(json.dumps({"ok": ok_all, "checks": checks}, indent=2))
    return 0 if ok_all else 1

if __name__ == "__main__":
    raise SystemExit(main())
