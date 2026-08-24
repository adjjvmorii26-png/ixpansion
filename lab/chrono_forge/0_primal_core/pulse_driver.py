#!/usr/bin/env python3
"""Global heartbeat with atomically persisted pulse state."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import json
import math
import time
from datetime import datetime, timezone

from lab.runtime_vault import read_json, state_path, write_json

STATE = state_path("pulse", "state.json")


def pulse(beats: int = 1) -> dict:
    state = read_json(STATE, {"beats": 0, "phase": 0.0})
    for _ in range(beats):
        state["beats"] = int(state.get("beats") or 0) + 1
        state["phase"] = (float(state.get("phase") or 0) + 0.6180339887) % (2 * math.pi)
        state["last"] = datetime.now(timezone.utc).isoformat()
        state["sigil"] = f"PULSE-{state['beats']:04X}"
        time.sleep(0.005)
    write_json(STATE, state)
    return state


def status() -> dict:
    return {"pulse": read_json(STATE, {})}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--beats", type=int, default=0)
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()
    if args.beats:
        print(json.dumps(pulse(args.beats), indent=2))
    if args.status or not args.beats:
        print(json.dumps(status(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
