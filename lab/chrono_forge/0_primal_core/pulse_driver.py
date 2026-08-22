#!/usr/bin/env python3
"""Global heartbeat — can proxy sandbox ticks or run a pure pulse."""
from __future__ import annotations
import argparse, json, math, time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE = HERE / "pulse_state.json"
SANDBOX = Path(__file__).resolve().parents[3] / "sandbox" / "sandbox_state.json"

def pulse(n: int = 1) -> dict:
    st = json.loads(STATE.read_text()) if STATE.exists() else {"beats": 0, "phase": 0.0}
    for _ in range(n):
        st["beats"] = int(st.get("beats") or 0) + 1
        st["phase"] = (float(st.get("phase") or 0) + 0.6180339887) % (2 * math.pi)
        st["last"] = datetime.now(timezone.utc).isoformat()
        st["sigil"] = f"PULSE-{st['beats']:04X}"
        time.sleep(0.005)
    STATE.write_text(json.dumps(st, indent=2) + "\n")
    return st

def status() -> dict:
    st = json.loads(STATE.read_text()) if STATE.exists() else {}
    sb = json.loads(SANDBOX.read_text()) if SANDBOX.exists() else {}
    return {"pulse": st, "sandbox_ticks": sb.get("ticks"), "entropy_budget": sb.get("entropy_budget")}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--beats", type=int, default=0)
    ap.add_argument("--status", action="store_true")
    a = ap.parse_args()
    if a.beats:
        print(json.dumps(pulse(a.beats), indent=2))
    if a.status or not a.beats:
        print(json.dumps(status(), indent=2))
