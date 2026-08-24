#!/usr/bin/env python3
"""Lab smoke with stderr capture; skip missing optional paths."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CF = ROOT / "lab" / "chrono_forge"
EXP = ROOT / "lab" / "experiments"

def run(cmd: list[str]) -> dict:
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    return {
        "ok": r.returncode == 0,
        "code": r.returncode,
        "out": (r.stdout or "")[-200:],
        "err": (r.stderr or "")[-200:],
    }

def main() -> int:
    checks = []
    ok_all = True
    targets = [
        ("pulse", CF / "0_primal_core" / "pulse_driver.py", ["--beats", "1"]),
        ("sentinel", CF / "2_agents" / "sentinel.py", []),
        ("recursion_reset", EXP / "recursion_anchor.py", ["reset"]),
        ("sandbox_status", ROOT / "sandbox" / "sandbox_engine.py", ["--status"]),
    ]
    for name, path, args in targets:
        if not path.exists():
            checks.append({"name": name, "ok": False, "err": f"missing {path}"})
            ok_all = False
            continue
        result = run([sys.executable, str(path)] + args)
        checks.append({"name": name, **result})
        ok_all &= result["ok"]
    print(json.dumps({"ok": ok_all, "checks": checks}, indent=2))
    return 0 if ok_all else 1

if __name__ == "__main__":
    raise SystemExit(main())
