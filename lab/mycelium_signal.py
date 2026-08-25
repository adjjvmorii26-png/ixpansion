#!/usr/bin/env python3
"""Mycelium Signal — model information propagation through the module network."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lab.astral_network_weaver import _load_registry, _registry_path
from lab.runtime_vault import (
    CHAIN_FIELDS,
    append_jsonl,
    ledger_path,
    read_json,
    state_path,
    write_json,
)

SCHEMA = "aleph.experiments.mycelium-signal.v1"
MAX_HOPS = 8
DECAY_BASE = 0.72
AMPLIFICATION = 1.15


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _hash(payload: dict[str, Any]) -> str:
    material = {k: v for k, v in payload.items() if k != "signal_hash"}
    return hashlib.sha256(_canonical(material)).hexdigest()


def _clamp(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 4)


def _capability_overlap(source_caps: list[str], target_caps: list[str]) -> float:
    if not source_caps or not target_caps:
        return 0.0
    shared = set(source_caps) & set(target_caps)
    return len(shared) / max(len(source_caps), len(target_caps))


def _propagate(
    source: str,
    modules: dict[str, Any],
    *,
    strength: float = 1.0,
    hops: int = MAX_HOPS,
    decay: float = DECAY_BASE,
    amplify: float = AMPLIFICATION,
) -> list[dict[str, Any]]:
    """BFS signal propagation through consuming edges with capability-based attenuation."""
    visited: set[str] = set()
    queue: list[tuple[str, float, int]] = [(source, strength, 0)]
    trace: list[dict[str, Any]] = []
    source_module = modules.get(source, {})

    while queue and len(trace) < hops * len(modules):
        current, current_strength, depth = queue.pop(0)
        if current in visited or depth > hops:
            continue
        visited.add(current)
        entry = modules.get(current, {})
        provides = entry.get("capabilities", [])
        consumes = entry.get("consumes", [])
        overlap = _capability_overlap(source_module.get("capabilities", []), provides)
        transmitted = current_strength * decay * (amplify if overlap > 0 else 1.0)
        transmitted = _clamp(transmitted)

        trace.append({
            "module": current,
            "depth": depth,
            "received_strength": current_strength,
            "transmitted_strength": transmitted,
            "capability_overlap": round(overlap, 4),
            "provides": provides,
            "consumes": consumes,
        })

        for target_name, target in modules.items():
            if target_name not in visited and any(c in target.get("consumes", []) for c in provides):
                queue.append((target_name, transmitted, depth + 1))

    return trace


def propagate_signal(
    source: str,
    *,
    strength: float = 1.0,
    hops: int = MAX_HOPS,
    clock: Any = utc_now,
    record: bool = True,
) -> dict[str, Any]:
    """Launch a signal from one module and trace its propagation through the network."""
    registry = _load_registry()
    modules = registry.get("modules", {})
    if source not in modules:
        raise ValueError(f"unknown source module: {source}")
    if not 1 <= hops <= MAX_HOPS:
        raise ValueError(f"hops must be between 1 and {MAX_HOPS}")

    trace = _propagate(source, modules, strength=strength, hops=hops)
    modules_reached = len([t for t in trace if t["module"] != source])
    strengths = [t["received_strength"] for t in trace]
    avg_strength = round(sum(strengths) / max(1, len(strengths)), 4)
    final_strengths = [t["transmitted_strength"] for t in trace]

    result: dict[str, Any] = {
        "schema": SCHEMA,
        "experiment": "mycelium-signal",
        "status": "sealed",
        "mode": "data-only-propagation-trace",
        "sealed_at": clock(),
        "source": source,
        "source_capabilities": modules[source].get("capabilities", []),
        "initial_strength": strength,
        "hops_requested": hops,
        "modules_reached": modules_reached,
        "trace_length": len(trace),
        "average_strength": avg_strength,
        "min_strength": round(min(strengths), 4) if strengths else 0,
        "max_strength": round(max(strengths), 4) if strengths else 0,
        "trace": trace,
        "execution_enabled": False,
    }
    result["signal_hash"] = _hash(result)

    if record:
        write_json(state_path("mycelium", "latest_signal.json"), {k: v for k, v in result.items() if k != "html"})
        append_jsonl(
            ledger_path(),
            {"type": "mycelium_signal", "ref": result["signal_hash"], "source": source, "reached": modules_reached},
        )
    return result


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source")
    p.add_argument("--strength", type=float, default=1.0)
    p.add_argument("--hops", type=int, default=MAX_HOPS)
    p.add_argument("--no-ledger", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = propagate_signal(args.source, strength=args.strength, hops=args.hops, record=not args.no_ledger)
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
