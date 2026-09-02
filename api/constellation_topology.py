"""Wave 219 — The Organism Sees Its Archipelago: Constellation Topology.

A topological eye over the whole bridge web: clusters repos by the
layers they share, detects which islands are choke-points (carrying
the most bridges), and maps the archipelago's shape — from scattered
islands to a single connected web.

Delivers: cluster map, per-repo centrality, articulation points
(islands whose removal would fragment the web), and a density index.
"""
from __future__ import annotations

import hashlib
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


def _adjacency(stones: List[Dict[str, Any]]) -> Dict[str, Set[str]]:
    """Build adjacent map: which rocks (arches) touch which islands."""
    adj: Dict[str, Set[str]] = defaultdict(set)
    for s in stones:
        adj[s["repo"]].add(s["organ"])
        adj[s["organ"]].add(s["repo"])
    return dict(adj)


def _articulation(adj: Dict[str, Set[str]]) -> Set[str]:
    """Find articulation points (islands whose removal disconnects the web)."""
    nodes = list(adj.keys())
    index_map: Dict[str, int] = {}
    low: Dict[str, int] = {}
    disc: Dict[str, int] = {}
    visited: Set[str] = set()
    time = [0]
    articulation: Set[str] = set()

    def dfs(u: str, parent: str = None):
        children = 0
        visited.add(u)
        disc[u] = low[u] = time[0]
        time[0] += 1
        for v in adj.get(u, ()):
            if v == parent:
                continue
            if v not in visited:
                children += 1
                dfs(v, u)
                low[u] = min(low[u], low[v])
                if parent is None and children > 1:
                    articulation.add(u)
                if parent is not None and low[v] >= disc[u]:
                    articulation.add(u)
            else:
                low[u] = min(low[u], disc[v])

    for n in nodes:
        if n not in visited:
            dfs(n)
    return articulation


def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "topology", "status": "mapping", "resonance": 0.9, "wave": 219}


def resonates_with() -> list:
    return ["topology", "archipelago", "cluster", "centrality", "articulation", "web", "density"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    action = payload.get("action", "map")
    ledger = _load_ledger()
    stones = ledger.get("stones", [])

    # per-repo degree (number of distinct organs / stones)
    by_repo: Dict[str, int] = defaultdict(int)
    organ_repos: Dict[str, Set[str]] = defaultdict(set)
    for s in stones:
        by_repo[s["repo"]] += 1
        organ_repos[s["organ"]].add(s["repo"])

    # compute adjacency + articulation
    adj = _adjacency(stones)
    articulation = _articulation(adj)

    # clusters: group repos by shared organ themes (crude: organ name prefix)
    clusters: Dict[str, List[str]] = defaultdict(list)
    for s in stones:
        organ = s["organ"]
        # derive a layer bucket from the organ name
        prefix = organ.split("_")[0] if "_" in organ else organ
        clusters[prefix].append(s["repo"])
    clusters = {k: sorted(set(v)) for k, v in clusters.items()}

    central = sorted(by_repo.items(), key=lambda x: -x[1])[:10]

    n_islands = len({s["repo"] for s in stones})
    n_organs = len({s["organ"] for s in stones})
    density = round(len(stones) / max(1, (n_islands * n_organs)), 4)

    if action == "clusters":
        return {"clusters": clusters, "n_clusters": len(clusters)}
    if action == "centrality":
        return {"central": [{"repo": r, "stones": c} for r, c in central]}
    if action == "articulation":
        return {"articulation_points": sorted(articulation), "count": len(articulation)}

    return {
        "status": "mapped",
        "islands": n_islands,
        "organs": n_organs,
        "density": density,
        "n_clusters": len(clusters),
        "central": [{"repo": r, "stones": c} for r, c in central],
        "articulation_points": sorted(articulation),
        "clusters": clusters,
        "note": "The archipelago is a web; some islands, removed, would unmake it.",
    }
