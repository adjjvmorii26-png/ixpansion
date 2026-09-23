"""Wave 908 — Temporal Echo.

Finds repeated fingerprints across ordered observations without treating
recurrence as causation, importance, or truth.
"""
from __future__ import annotations

import hashlib, json
from collections import defaultdict
from typing import Any, Dict, List


def fingerprint(record: Dict[str, Any]) -> str:
    value = record.get("fingerprint", record.get("result_digest", record))
    raw = json.dumps(value, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def echo_map(records: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    records = records or []
    buckets: Dict[str, List[int]] = defaultdict(list)
    for index, record in enumerate(records):
        buckets[fingerprint(record)].append(index)

    echoes = []
    for fp, positions in sorted(buckets.items()):
        if len(positions) > 1:
            gaps = [b - a for a, b in zip(positions, positions[1:])]
            echoes.append({
                "fingerprint": fp,
                "positions": positions,
                "occurrences": len(positions),
                "gaps": gaps,
            })

    return {
        "wave": 908,
        "name": "temporal_echo",
        "record_count": len(records),
        "unique_fingerprints": len(buckets),
        "echo_count": len(echoes),
        "echoes": echoes,
        "interpretation_boundary": "recurrence is descriptive; it is not evidence of causation",
        "replayable": True,
    }


def handler(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    return echo_map(payload.get("records", []))


def coherence_vitals() -> dict:
    return {"layer": "experimental", "status": "active", "wave": "908", "module": "temporal_echo"}


def resonates_with() -> list:
    return ["wave907_branch_atlas", "wave906_evolution_map", "wave905_lineage_graph"]
