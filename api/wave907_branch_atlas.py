"""Wave 907 — Branch Atlas.

Deterministically summarizes branch topology from lineage-style records.
It describes structure only; it does not rank branches or infer causation.
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
    by_id: Dict[str, Dict[str, Any]] = {}
    for record in records:
        rid = str(record.get("record_digest") or _id(record))
        by_id.setdefault(rid, record)

    ids = sorted(by_id)
    parent = {
        rid: str(record["parent"])
        for rid, record in by_id.items()
        if record.get("parent")
    }

    children: Dict[str, List[str]] = {rid: [] for rid in ids}
    for child, ancestor in parent.items():
        children.setdefault(ancestor, []).append(child)
    for values in children.values():
        values.sort()

    known = set(ids)
    roots = sorted(rid for rid in ids if rid not in parent)
    orphan_parents = sorted({ancestor for ancestor in parent.values() if ancestor not in known})

    depth: Dict[str, int] = {}

    def visit(rid: str, trail: set[str]) -> int:
        if rid in depth:
            return depth[rid]
        if rid in trail:
            return 0
        ancestor = parent.get(rid)
        if not ancestor or ancestor not in known:
            depth[rid] = 0
        else:
            depth[rid] = visit(ancestor, trail | {rid}) + 1
        return depth[rid]

    for rid in ids:
        visit(rid, set())

    branch_points = [
        {"node": rid, "children": len(children[rid]), "children_ids": children[rid]}
        for rid in ids
        if len(children[rid]) > 1
    ]
    leaves = sorted(rid for rid in ids if not children.get(rid))

    terminal_paths = []
    for leaf in leaves:
        path = [leaf]
        seen = {leaf}
        current = leaf
        while current in parent:
            ancestor = parent[current]
            if ancestor not in known or ancestor in seen:
                break
            path.append(ancestor)
            seen.add(ancestor)
            current = ancestor
        path.reverse()
        terminal_paths.append({
            "leaf": leaf,
            "root": path[0],
            "depth": depth.get(leaf, 0),
            "path": path,
        })

    return {
        "wave": 907,
        "name": "branch_atlas",
        "node_count": len(ids),
        "edge_count": len(parent),
        "roots": roots,
        "leaves": leaves,
        "branch_points": branch_points,
        "depth": {rid: depth[rid] for rid in ids},
        "terminal_paths": sorted(terminal_paths, key=lambda item: item["leaf"]),
        "orphan_parents": orphan_parents,
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
            "wave": 907,
            "name": "branch_atlas",
            "purpose": "descriptive branch topology",
        }
    return {"error": "unknown action", "available": ["status", "build"]}


def coherence_vitals() -> dict:
    return {"layer": "experimental", "status": "active", "wave": "907", "module": "branch_atlas"}


def resonates_with() -> list:
    return ["wave906_evolution_map", "wave905_lineage_graph", "wave904_evidence_ledger"]
