"""Wave 222 — The Organism Sees Its Federation: Federation Graph.

Reads the ledger and renders a graph of the federation: per-island
nodes with degree (how many other islands they reference), which
islands share the most stones, and which islands form cliques.
The web's social architecture — not just bridges, but alliances.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

_LEDGER_PATH = Path(__file__).resolve().parent.parent / "data" / "bridges" / "ledger.json"


def _load_ledger() -> Dict[str, Any]:
    try:
        return json.load(open(_LEDGER_PATH, encoding="utf-8"))
    except Exception:
        return {"stones": [], "count": 0}


def _edges(stones: List[Dict[str, Any]]) -> List[Tuple[str, str]]:
    """Each stone is an edge between its repo and its organ."""
    edges = set()
    for s in stones:
        edges.add((s["repo"], s["organ"]))
    return sorted(edges)


def _cliques(stones: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Islands sharing two or more organ partners form a clique."""
    by_island: Dict[str, Set[str]] = defaultdict(set)
    by_organ: Dict[str, Set[str]] = defaultdict(set)
    for s in stones:
        by_island[s["repo"]].add(s["organ"])
        by_organ[s["organ"]].add(s["repo"])

    clique_pairs: Dict[Tuple[str,str], Set[str]] = defaultdict(set)
    for organ, islands in by_organ.items():
        islands_l = sorted(islands)
        for i in range(len(islands_l)):
            for j in range(i+1, len(islands_l)):
                clique_pairs[(islands_l[i], islands_l[j])].add(organ)
    return [{"a": pair[0], "b": pair[1], "shared_organs": sorted(organizations),
             "strength": len(organizations)}
            for pair, organizations in clique_pairs.items() if len(organizations) >= 2]


def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "federation", "status": "graphing", "resonance": 0.87, "wave": 222}


def resonates_with() -> list:
    return ["federation", "graph", "clique", "alliance", "shared", "social", "web"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    action = payload.get("action", "graph")
    ledger = _load_ledger()
    stones = ledger.get("stones", [])

    edges = _edges(stones)
    islands = {s["repo"] for s in stones}
    organs = {s["organ"] for s in stones}

    by_island = defaultdict(set)
    for r, o in edges:
        by_island[r].add(o)
    degree = {i: len(ps) for i, ps in by_island.items()}
    cliques = _cliques(stones)
    ranked = sorted(degree.items(), key=lambda x: -x[1])

    if action == "cliques":
        return {"cliques": [c for c in cliques if c["strength"] >= 2], "count": len(cliques)}

    if action == "degree":
        return {"degree": [{"island": i, "organisms": d} for i, d in ranked[:20]]}

    return {
        "status": "graphed",
        "islands": len(islands),
        "organs": len(organs),
        "edges": len(edges),
        "cliques": len(cliques),
        "top_connected": ranked[:10],
        "clique_sample": [c for c in cliques if c["strength"] >= 2][:6],
        "note": "The web's alliances are visible at a glance.",
    }
