#!/usr/bin/env python3
"""Flux world — mutate a seed hash each run."""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

STATE = Path(__file__).resolve().parent / "flux_state.json"

def step() -> dict:
    st = json.loads(STATE.read_text()) if STATE.exists() else {"gen": 0, "seed": "flux-0"}
    gen = int(st.get("gen") or 0) + 1
    seed = hashlib.sha256(f"{st.get('seed')}-{gen}".encode()).hexdigest()[:16]
    out = {"world": "sandbox_flux", "gen": gen, "seed": seed,
           "ts": datetime.now(timezone.utc).isoformat()}
    STATE.write_text(json.dumps(out, indent=2) + "\n")
    return out

if __name__ == "__main__":
    print(json.dumps(step(), indent=2))
