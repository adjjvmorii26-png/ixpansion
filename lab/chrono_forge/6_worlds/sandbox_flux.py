#!/usr/bin/env python3
"""Flux world — mutate a deterministic seed lineage each generation."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import hashlib
import json
from datetime import datetime, timezone

from lab.runtime_vault import read_json, state_path, write_json

STATE = state_path("worlds", "flux.json")


def step() -> dict:
    state = read_json(STATE, {"gen": 0, "seed": "flux-0"})
    generation = int(state.get("gen") or 0) + 1
    seed = hashlib.sha256(f"{state.get('seed')}-{generation}".encode()).hexdigest()[:16]
    result = {"world": "sandbox_flux", "gen": generation, "seed": seed,
              "ts": datetime.now(timezone.utc).isoformat()}
    write_json(STATE, result)
    return result


if __name__ == "__main__":
    print(json.dumps(step(), indent=2))
