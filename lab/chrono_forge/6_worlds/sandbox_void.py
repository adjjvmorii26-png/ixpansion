#!/usr/bin/env python3
"""Void world — intentional null ops for baseline timing."""
from __future__ import annotations
import json, time
from datetime import datetime, timezone
from pathlib import Path

STATE = Path(__file__).resolve().parent / "void_state.json"

def run(n: int = 1000) -> dict:
    t0 = time.perf_counter()
    x = 0
    for i in range(n):
        x ^= i
    elapsed_ms = (time.perf_counter() - t0) * 1000
    out = {"world": "sandbox_void", "ops": n, "xor_sink": x,
           "elapsed_ms": round(elapsed_ms, 4),
           "ts": datetime.now(timezone.utc).isoformat()}
    STATE.write_text(json.dumps(out, indent=2) + "\n")
    return out

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
