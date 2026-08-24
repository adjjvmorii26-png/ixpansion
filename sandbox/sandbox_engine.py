#!/usr/bin/env python3
"""IXPANSION sandbox engine — ticks, entropy budget, status."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import argparse, json, math, time
from datetime import datetime, timezone
from pathlib import Path

from lab.runtime_vault import append_jsonl, ledger_path, read_json, state_path, write_json

STATE = state_path("sandbox", "engine.json")
PROOF = ledger_path()

def load_state() -> dict:
    return read_json(STATE, {"ticks": 0, "started_at": None, "last_tick_at": None,
                             "status": "idle", "history": [], "entropy_budget": 1.0,
                             "novelty": 0.0, "phase": 0.0})

def save_state(state: dict) -> None:
    write_json(STATE, state)

def _append_proof(kind: str, ref: str, **extra) -> None:
    append_jsonl(PROOF, {"ts": datetime.now(timezone.utc).isoformat(), "type": kind,
                         "ref": ref, **extra})

def _tick_signal(tick: int, phase: float) -> dict:
    t = tick * 0.1
    a = math.sin(2 * math.pi * 0.7 * t + phase)
    b = math.sin(2 * math.pi * 1.3 * t + phase * 0.5)
    energy = 0.5 * (a * a + b * b)
    return {"a": round(a, 5), "b": round(b, 5), "energy": round(energy, 5)}

def run_ticks(n: int, proof: bool = True) -> dict:
    st = load_state()
    now = datetime.now(timezone.utc).isoformat()
    if not st.get("started_at"):
        st["started_at"] = now
    st["status"] = "running"
    budget = float(st.get("entropy_budget") or 1.0)
    phase = float(st.get("phase") or 0.0)
    for _ in range(n):
        st["ticks"] = int(st.get("ticks") or 0) + 1
        st["last_tick_at"] = datetime.now(timezone.utc).isoformat()
        sig = _tick_signal(st["ticks"], phase)
        budget = max(0.05, budget - 0.01 * sig["energy"])
        phase = (phase + 0.17 + 0.05 * sig["a"]) % (2 * math.pi)
        novelty = abs(sig["a"] - sig["b"])
        st["entropy_budget"] = round(budget, 4)
        st["phase"] = round(phase, 4)
        st["novelty"] = round(novelty, 4)
        hist = st.setdefault("history", [])
        hist.append({"tick": st["ticks"], **sig})
        st["history"] = hist[-50:]
        time.sleep(0.005)
        print(f"tick {st['ticks']} energy={sig['energy']:.3f}")
    st["status"] = "idle"
    save_state(st)
    if proof:
        _append_proof("sandbox_ticks", f"ticks+{n}", total_ticks=st["ticks"])
    return st

def status() -> dict:
    st = load_state()
    out = {"status": st.get("status", "idle"), "ticks": st.get("ticks", 0),
           "entropy_budget": st.get("entropy_budget"), "novelty": st.get("novelty")}
    print(json.dumps(out, indent=2))
    return out

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--ticks", type=int, default=0)
    p.add_argument("--status", action="store_true")
    p.add_argument("--no-proof", action="store_true")
    args = p.parse_args()
    if args.ticks > 0:
        run_ticks(args.ticks, proof=not args.no_proof)
    if args.status or args.ticks == 0:
        status()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
