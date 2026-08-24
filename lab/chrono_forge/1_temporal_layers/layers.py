#!/usr/bin/env python3
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
STATE = Path(__file__).resolve().parent / "layer_state.json"
def step(present: str) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    st = json.loads(STATE.read_text()) if STATE.exists() else {"gamma": []}
    beta = f"shadow:{present[::-1][:40]}"
    gamma = st.get("gamma") or []
    delta = {"paradox": "echo_collision", "value": present[:40]} if present in [g.get("echo") for g in gamma] else None
    gamma.append({"ts": now, "echo": present[:80]})
    STATE.write_text(json.dumps({"gamma": gamma[-20:]}, indent=2) + "\n")
    return {"alpha": present, "beta": beta, "gamma_len": len(gamma), "delta": delta, "ts": now}
if __name__ == "__main__":
    import sys
    print(json.dumps(step(" ".join(sys.argv[1:]) or "mesh ships"), indent=2))
