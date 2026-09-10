#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
SE = Path(__file__).resolve().parent.parent
def test():
    inj = subprocess.run([sys.executable, str(SE / "CHAOS_LAYER" / "fault_injector.py"), "negate_ethics"], capture_output=True, text=True)
    fault = json.loads(inj.stdout or "{}")
    ethics_ok = bool((fault.get("record") or {}).get("ethics_ok", False))
    r = subprocess.run([sys.executable, str(SE / "EMERGENT_LAYER" / "reasoning" / "reason_engine.py")] + ([] if ethics_ok else ["fail"]), capture_output=True, text=True)
    decision = json.loads(r.stdout or "{}")
    passed = (not ethics_ok) and decision.get("action") == "hold"
    return {"ok": passed, "fault": fault.get("fault"), "ethics_ok": ethics_ok, "action": decision.get("action"), "test": "chaos_implies_hold"}
if __name__ == "__main__":
    out = test()
    print(json.dumps(out, indent=2))
    raise SystemExit(0 if out["ok"] else 1)
