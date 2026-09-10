#!/usr/bin/env python3
"""CHRONOFORGE portal."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent

def main() -> int:
    act = (sys.argv[1] if len(sys.argv) > 1 else "help").lower()
    if act in ("help", "-h", "--help"):
        print(json.dumps({"acts": ["invariants", "epoch", "transition-plan", "boot", "ethics"], "usage": "python cf_portal.py <act> [target_epoch]"}, indent=2))
        return 0
    if act == "invariants":
        r = subprocess.run([sys.executable, str(ROOT / "invariant_engine.py")], capture_output=True, text=True)
        print(r.stdout or r.stderr)
        return r.returncode
    if act in ("transition-plan", "transition_plan", "etp"):
        target = sys.argv[2] if len(sys.argv) > 2 else "E2"
        r = subprocess.run([sys.executable, str(ROOT / "epoch_transition.py"), target], capture_output=True, text=True)
        print(r.stdout or r.stderr)
        return r.returncode
    if act == "epoch":
        p = ROOT.parent / "000_ROOT_SPEC" / "timeline_epochs.yaml"
        print(p.read_text() if p.exists() else json.dumps({"ok": False}))
        return 0
    if act == "ethics":
        issues = []
        inv = ROOT.parent / "000_ROOT_SPEC" / "invariants.hex"
        if not inv.exists():
            issues.append("invariants_missing")
        print(json.dumps({"ok": not issues, "issues": issues, "mandatory": True}, indent=2))
        return 0 if not issues else 1
    if act == "boot":
        steps = []
        ok = True
        for name in ("ethics", "invariants"):
            r = subprocess.run([sys.executable, str(ROOT / "cf_portal.py"), name], capture_output=True, text=True)
            steps.append({"step": name, "ok": r.returncode == 0})
            ok &= r.returncode == 0
        print(json.dumps({"boot": True, "ok": ok, "steps": steps}, indent=2))
        return 0 if ok else 1
    print(json.dumps({"ok": False, "err": "unknown"}))
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
