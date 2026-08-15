#!/usr/bin/env python3
"""Edge-native spatial sharding protocol for lattice grids."""
from __future__ import annotations
import json
from typing import Dict, List, Tuple
from swarm_wasm_lattice import run_wasm_lattice


def shard_bounds(n: int, num_shards: int) -> List[Tuple[int, int]]:
    """Return [start, end) row ranges for 1D row sharding."""
    num_shards = max(1, min(num_shards, n))
    size = n // num_shards
    bounds = []
    for i in range(num_shards):
        start = i * size
        end = n if i == num_shards - 1 else (i + 1) * size
        bounds.append((start, end))
    return bounds


def run_sharded(n: int = 24, steps: int = 15, seed: float = 0.3, shards: int = 4) -> dict:
    """
    Simulate distributed shard execution by running full grid then
    attaching shard metadata (real deploy: each edge owns a row range).
    """
    result = run_wasm_lattice(n=n, steps=steps, seed=seed)
    bounds = shard_bounds(n, shards)
    result["spatial_shards"] = [
        {"shard_id": i, "rows": [a, b], "owner_hint": f"edge-{i}"}
        for i, (a, b) in enumerate(bounds)
    ]
    result["protocol"] = "spatial_shard_v1"
    return result


if __name__ == "__main__":
    print(json.dumps(run_sharded(), indent=2, default=str)[:800])


def adaptive_shard_plan(n: int, worker_loads: dict, min_rows: int = 2) -> list:
    """
    worker_loads: {worker_id: cpu_0_to_1}
    Allocate more rows to lower-load workers.
    """
    if not worker_loads:
        return [{"shard_id": 0, "rows": [0, n], "owner_hint": "local", "load": 0.0}]
    # inverse-load weights
    weights = {}
    for w, load in worker_loads.items():
        weights[w] = max(0.05, 1.0 - float(load))
    total = sum(weights.values())
    plan = []
    cursor = 0
    workers = list(weights.keys())
    for i, w in enumerate(workers):
        share = weights[w] / total
        rows = max(min_rows, int(round(n * share)))
        if i == len(workers) - 1:
            end = n
        else:
            end = min(n, cursor + rows)
        if cursor >= n:
            break
        plan.append({
            "shard_id": i,
            "rows": [cursor, end],
            "owner_hint": w,
            "load": worker_loads[w],
            "weight": round(weights[w], 4),
        })
        cursor = end
    if plan and plan[-1]["rows"][1] < n:
        plan[-1]["rows"][1] = n
    return plan


def run_adaptive(n: int = 24, steps: int = 15, seed: float = 0.3, worker_loads: dict = None) -> dict:
    worker_loads = worker_loads or {"edge-0": 0.8, "edge-1": 0.2, "edge-2": 0.5, "edge-3": 0.1}
    plan = adaptive_shard_plan(n, worker_loads)
    result = run_wasm_lattice(n=n, steps=steps, seed=seed)
    result["spatial_shards"] = plan
    result["protocol"] = "spatial_shard_adaptive_v1"
    return result


if __name__ == "__main__" and False:
    pass
  
