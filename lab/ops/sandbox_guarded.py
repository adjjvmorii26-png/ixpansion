#!/usr/bin/env python3
"""Sandbox ticks only if epoch ticket mode == act."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
def main():
    v = subprocess.run([sys.executable, str(REPO / "lab" / "ops" / "epoch_ticket.py"), "verify"], capture_output=True, text=True)
    try: info = json.loads(v.stdout or "{}")
    except json.JSONDecodeError: info = {"mode": "hold"}
    mode = info.get("mode", "hold")
    eng = REPO / "sandbox" / "sandbox_engine.py"
    if mode != "act":
        print(json.dumps({"ok": True, "skipped_ticks": True, "mode": mode, "reason": "epoch_ticket_not_act", "hint": "python lab/ops/epoch_ticket.py issue"}, indent=2))
        if eng.exists(): subprocess.run([sys.executable, str(eng), "--status"])
        return 0
    ticks = sys.argv[1] if len(sys.argv) > 1 else "5"
    if eng.exists():
        r = subprocess.run([sys.executable, str(eng), "--ticks", ticks], capture_output=True, text=True)
        print(r.stdout or r.stderr); return r.returncode
    print(json.dumps({"ok": False, "err": "no_sandbox_engine"})); return 1
if __name__ == "__main__":
    raise SystemExit(main())
