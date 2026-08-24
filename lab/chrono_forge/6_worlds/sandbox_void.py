#!/usr/bin/env python3
"""Void world — intentional null operations for baseline timing."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import json
import time
from datetime import datetime, timezone

from lab.runtime_vault import state_path, write_json

STATE = state_path("worlds", "void.json")


def run(operations: int = 1000) -> dict:
    started = time.perf_counter()
    sink = 0
    for value in range(operations):
        sink ^= value
    result = {"world": "sandbox_void", "ops": operations, "xor_sink": sink,
              "elapsed_ms": round((time.perf_counter() - started) * 1000, 4),
              "ts": datetime.now(timezone.utc).isoformat()}
    write_json(STATE, result)
    return result


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
