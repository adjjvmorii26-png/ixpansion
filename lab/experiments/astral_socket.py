#!/usr/bin/env python3
"""Lightweight message bus via JSONL astral channel."""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path

CHAN = Path(__file__).resolve().parent / "astral_channel.jsonl"

def send(topic: str, payload: dict) -> dict:
    rec = {"ts": datetime.now(timezone.utc).isoformat(), "topic": topic, "payload": payload}
    with CHAN.open("a") as f:
        f.write(json.dumps(rec) + "\n")
    return rec

def tail(n: int = 10) -> list:
    if not CHAN.exists():
        return []
    return [json.loads(x) for x in CHAN.read_text().strip().splitlines()[-n:] if x.strip()]

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "tail":
        print(json.dumps(tail(), indent=2))
    else:
        root = Path(__file__).resolve().parents[2]
        pulse = root / "lab" / "chrono_forge" / "0_primal_core" / "pulse_state.json"
        sb = root / "sandbox" / "sandbox_state.json"
        p = json.loads(pulse.read_text()) if pulse.exists() else {}
        s = json.loads(sb.read_text()) if sb.exists() else {}
        print(json.dumps(send("pulse_sandbox_bridge", {
            "pulse_sigil": p.get("sigil"), "beats": p.get("beats"),
            "ticks": s.get("ticks"), "novelty": s.get("novelty"),
            "entropy_budget": s.get("entropy_budget"),
        }), indent=2))
