#!/usr/bin/env python3
"""Entropy weather from sandbox history — novelty climate."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "sandbox" / "sandbox_state.json"
OUT = Path(__file__).resolve().parent / "entropy_weather.json"

def forecast() -> dict:
    if not STATE.exists():
        return {"ok": False, "sky": "unknown"}
    st = json.loads(STATE.read_text())
    hist = st.get("history") or []
    energies = [h.get("energy", 0) for h in hist[-20:]]
    avg = sum(energies) / max(len(energies), 1)
    budget = float(st.get("entropy_budget") or 1)
    novelty = float(st.get("novelty") or 0)
    if budget > 0.8 and novelty < 0.3:
        sky = "calm"
    elif budget < 0.3:
        sky = "storm"
    elif novelty > 0.6:
        sky = "aurora"
    else:
        sky = "breezy"
    out = {"ok": True, "sky": sky, "budget": budget, "novelty": novelty,
           "avg_energy_20": round(avg, 4), "ticks": st.get("ticks")}
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return out

if __name__ == "__main__":
    forecast()
