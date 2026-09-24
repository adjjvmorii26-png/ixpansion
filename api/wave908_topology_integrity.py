"""Wave 908 — Topology Integrity.

Deterministically reports structural integrity anomalies in lineage records.
It describes malformed or incomplete topology; it does not rank, infer causation,
or declare semantic truth.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List


def _id(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def build(records: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    records = records or []
    ids_seen: Dict[str, int] = {}
    by_id: Dict[str, Dict[str, Any]] = {}
    duplicate_ids: List[str] = []

    for record in records:
        rid = str(record.get("record_digest") or _id(record))
        ids_seen[rid] = ids_seen.get(rid, 0) + 1
        if rid in by_id:
            duplicate_ids.append(rid)
        else:
            by_id[rid] = record

    ids = sorted(by_id)
    known = set(ids)
    parents = {
        rid: str(record["parent"])
        for rid, record in by_id.items()
        if record.get("parent")
    }

    orphan_parents = sorted({p for p in parents.values() if p not in known})
    self_cycles = sorted(rid for rid, parent in parents.items() if rid == parent)

    cycles: set[tuple[str, ...]] = set()
    for start in ids:
        path: List[str] = []
        positions: Dict[str, int] = {}
        current = start
        while current in parents and current in known:
            if current in positions:
                cycle = tuple(path[positions[current] :])
                if cycle:
                    rotations = [
                        cycle[i:] + cycle[:i] for i in range(len(cycle))
                    ]
                    cycles.add(min(rotations))
                break
            positions[current] = len(path)
            path.append(current)
            current = parents[current]

    cycle_paths = [list(cycle) for cycle in sorted(cycles)]

    # The current lineage schema permits one parent per record. Convergence
    # therefore cannot be represented as a true multi-parent edge.
    schema_limits = ["single_parent_model"]

    duplicate_ids = sorted(set(duplicate_ids))
    anomaly_count = (
        len(duplicate_ids)
        + len(self_cycles)
        + len(cycle_paths)
        + len(orphan_parents)
    )

    fingerprint = _id(
        {
            "duplicates": duplicate_ids,
            "self_cycles": self_cycles,
            "cycles": cycle_paths,
            "orphan_parents": orphan_parents,
            "schema_limits": schema_limits,
        }
    )

    return {
        "wave": 908,
        "name": "topology_integrity",
        "node_count": len(ids),
        "anomaly_count": anomaly_count,
        "duplicate_ids": duplicate_ids,
        "self_cycles": self_cycles,
        "cycles": cycle_paths,
        "orphan_parents": orphan_parents,
        "schema_limits": schema_limits,
        "integrity_fingerprint": fingerprint,
        "replayable": True,
    }


def handler(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    action = payload.get("action", "status")
    if action == "build":
        return build(payload.get("records", []))
    if action == "status":
        return {
            "status": "experimental",
            "wave": 908,
            "name": "topology_integrity",
            "purpose": "descriptive topology integrity diagnostics",
        }
    return {"error": "unknown action", "available": ["status", "build"]}


def coherence_vitals() -> dict:
    return {
        "layer": "experimental",
        "status": "active",
        "wave": "908",
        "module": "topology_integrity",
    }


def resonates_with() -> list:
    return [
        "wave907_branch_atlas",
        "wave906_evolution_map",
        "wave905_lineage_graph",
    ]
