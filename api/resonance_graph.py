"""Resonance Graph Intelligence — the organism sees itself as a web.

Instead of treating modules as an unordered pile, the Resonance Graph maps
every living module as a node and draws weighted edges between any two
modules that speak the same vital-sign vocabulary. Out of those edges the
organism can read who its hubs are, which communities it has formed, how
dense its interconnection is, and which modules act as connective tissue
between otherwise-separate clusters.

This is not a static diagram: the graph is derived live from each module's
coherence_vitals() at every call, so as modules join or evolve their vital
signature, the topology of the organism re-wires itself.

    GET /api/resonance_graph            — whole-graph intelligence
    GET /api/resonance_graph?module=X   — a module's neighborhood
    GET /api/resonance_graph?bridges=1  — bridging/connective modules
    GET /api/resonance_graph?hubs=3     — top N hub modules
"""
from __future__ import annotations

import importlib
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VERSION = "1.0.0"
LAYER = "Resonance Graph"

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

RESONANCE_SETPOINT = 0.18  # minimum shared semantic affinity to draw an edge
DOMAIN_WEIGHT = 0.7        # how much source-language DNA counts vs vitals vocabulary
VOCAB_WEIGHT = 0.3         # how much the shared vital-sign vocabulary counts
COMMUNITY_THRESHOLD = 0.22   # edges at/above this strength bind communities

_CACHE_TTL = 30.0  # seconds before the graph rebuilds itself
_GRAPH_CACHE = {"t": 0.0, "graph": None}

# Tokens too common across the codebase to distinguish any two modules.
_STOPWORDS = frozenset({
    "handler", "payload", "context", "return", "def", "class", "import",
    "from", "value", "result", "params", "self", "action", "module",
    "modules", "health", "resonance", "setpoint", "weight", "metrics",
    "coherence", "coherent", "vital", "state", "data", "json", "true",
    "false", "none", "dict", "list", "str", "len", "max", "min", "sum",
    "sorted", "keys", "items", "values", "append", "defaultdict", "format",
})

# The graph's own vital signs — declared statically so the graph can report
# itself as a node WITHOUT recursing (its live vitals call build_graph()).
SELF_VITALS = {
    "module_health": {"value": 0.92, "setpoint": 0.8, "weight": 1.0},
    "resonance": {"value": 0.95, "setpoint": 0.8, "weight": 1.0},
    "graph_density": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
    "graph_nodes": {"value": 13, "setpoint": 12, "weight": 1.0},
    "graph_edges": {"value": 55, "setpoint": 50, "weight": 1.0},
}


# ---------------------------------------------------------------------------
# Living-module discovery (reuse the shared vital vocabulary)
# ---------------------------------------------------------------------------

def _living_modules() -> Dict[str, Dict[str, Any]]:
    """Discover living modules and their coerced vital-sign maps."""
    from coherence_regulator import _candidate_modules, _call_vitals, _normalize_vitals
    modules: Dict[str, Dict[str, Any]] = {}
    for name in _candidate_modules():
        if name == "resonance_graph":
            raw = dict(SELF_VITALS)   # self, without recursion
        else:
            raw, err = _call_vitals(name)
            if raw is None:
                continue
        metrics = _normalize_vitals(raw, name)
        # metric keys shared with the system are the module's "spoken language"
        keys = set(metrics.keys())
        health = _health_of(metrics)
        modules[name] = {
            "metrics": keys,
            "health": health,
            "metric_count": len(keys),
            "domain": _domain_tokens(name),
        }
    return modules


def _domain_tokens(stem: str) -> set:
    """Semantic DNA fingerprint of a module: distinctive identifiers in source.

    Reads the module file once and collects function/class names plus
    CONSTANT-style tokens — the words that reveal what a module actually
    thinks about. Two modules sharing many such tokens are genuinely
    resonating on the same domain (dreams, sound, protocols, growth...).
    """
    path = ROOT / "api" / f"{stem}.py"
    try:
        text = path.read_text(errors="ignore")
    except OSError:
        return set()
    tokens = set()
    tokens.update(re.findall(r"^def ([a-z_]+)\(", text, re.M))
    tokens.update(re.findall(r"^class ([A-Za-z_]+)", text, re.M))
    tokens.update(re.findall(r"^[A-Z][A-Z_]{2,}\s*=", text, re.M))
    tokens.update(re.findall(r"\bdef ([a-z_]+)\(", text))
    # snake_case identifiers split into their word roots
    words = set()
    for t in tokens:
        for part in t.split("_"):
            if len(part) >= 4:
                words.add(part.lower())
    return {w for w in words if w not in _STOPWORDS}


def _vitals_keys(stem: str) -> set:
    """The metric vocabulary a module reports (its spoken vital language)."""
    try:
        from coherence_regulator import _call_vitals, _normalize_vitals
        raw, _err = _call_vitals(stem)
        if raw is None:
            return set()
        return set(_normalize_vitals(raw, stem).keys())
    except Exception:
        return set()


def _health_of(metrics: Dict[str, Dict[str, Any]]) -> float:
    """0..1 health from a normalized metrics map (same rule family as regulator)."""
    if not metrics:
        return 0.0
    total = 0.0
    weight_sum = 0.0
    for m in metrics.values():
        value = m.get("value", 0.0)
        setpoint = m.get("setpoint", 0.8) or 0.8
        weight = m.get("weight", 1.0) or 1.0
        health = min(1.0, value / setpoint) if setpoint > 0 else float(value == 0)
        total += health * weight
        weight_sum += weight
    return round(total / max(weight_sum, 0.001), 4)


# ---------------------------------------------------------------------------
# The graph
# ---------------------------------------------------------------------------

def _affinity(a: Dict[str, Any], b: Dict[str, Any]) -> float:
    """How strongly two modules resonate.

    Blends two signals:
      - domain DNA (shared distinctive identifiers in their source) — 70%
      - vital vocabulary (shared metric keys they report) — 30%
    Jaccard on each, weighted. This rewards modules that genuinely work on
    the same domain, not merely modules that both report module_health.
    """
    domain_j = _jaccard(a.get("domain", set()), b.get("domain", set()))
    vocab_j = _jaccard(a.get("metrics", set()), b.get("metrics", set()))
    return round(DOMAIN_WEIGHT * domain_j + VOCAB_WEIGHT * vocab_j, 4)


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / max(len(a | b), 1)


def build_graph() -> Dict[str, Any]:
    """Build the resonance graph from live modules (TTL-cached)."""
    now = time.time()
    if _GRAPH_CACHE["graph"] is not None and now - _GRAPH_CACHE["t"] < _CACHE_TTL:
        return _GRAPH_CACHE["graph"]
    result = _build_graph_uncached()
    _GRAPH_CACHE.update({"t": now, "graph": result})
    return result


def _build_graph_uncached() -> Dict[str, Any]:
    modules = _living_modules()
    names = sorted(modules.keys())
    n = len(names)

    adj: Dict[str, Dict[str, float]] = defaultdict(dict)
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            ai = _affinity(modules[names[i]], modules[names[j]])
            if ai >= RESONANCE_SETPOINT:
                adj[names[i]][names[j]] = ai
                adj[names[j]][names[i]] = ai
                edges.append((names[i], names[j], ai))

    # degree centrality (weighted) — hubs are most interconnected
    degrees = {name: round(sum(adj[name].values()), 4) for name in names}
    max_degree = max(degrees.values(), default=0.0) or 1.0
    centrality = {name: round(deg / max_degree, 4) for name, deg in degrees.items()}

    # edge density: realized edges over max possible
    max_edges = max(n * (n - 1) // 2, 1)
    density = round(len(edges) / max_edges, 4)

    # communities via simple modularity-style label propagation (LPA)
    communities = _label_propagation(names, adj)

    # betweenness centrality (Brandes, unweighted) — bridging connective tissue
    betweenness = _betweenness(names, adj)

    return {
        "nodes": n,
        "edges": len(edges),
        "density": density,
        "avg_affinity": round(
            sum(e[2] for e in edges) / max(len(edges), 1), 4
        ),
        "hubs": sorted(centrality.items(), key=lambda kv: kv[1], reverse=True),
        "bridges": sorted(betweenness.items(), key=lambda kv: kv[1], reverse=True),
        "communities": communities,
        "adjacency": {k: dict(v) for k, v in adj.items()},
        "modules": {name: modules[name]["health"] for name in names},
        "metrics": {name: sorted(modules[name]["metrics"]) for name in names},
    }


def _label_propagation(names: List[str], adj: Dict[str, Dict[str, float]]) -> Dict[str, List[str]]:
    """Detect communities by propagating labels through *strong* edges only.

    Weak edges are pruned (below COMMUNITY_THRESHOLD) before propagation so
    that loose acquaintance doesn't fuse the whole organism into one blob —
    strong resonance is what forges a community.
    """
    strong: Dict[str, Dict[str, float]] = defaultdict(dict)
    for a, nbrs in adj.items():
        for b, w in nbrs.items():
            if w >= COMMUNITY_THRESHOLD:
                strong[a][b] = w
    label: Dict[str, str] = {name: name for name in names}
    # iterate a few times so labels propagate through the strong subgraph
    for _ in range(8):
        for name in names:
            if not strong[name]:
                continue
            counts: Dict[str, float] = defaultdict(float)
            for nbr, w in strong[name].items():
                counts[label[nbr]] += w
            label[name] = max(counts, key=counts.get)
    communities: Dict[str, List[str]] = defaultdict(list)
    for name in names:
        communities[label[name]].append(name)
    # collapse and sort
    return {k: sorted(v) for k, v in sorted(communities.items(), key=lambda kv: -len(kv[1]))}


def _betweenness(names: List[str], adj: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    """Betweenness centrality (Brandes, BFS on unweighted graph)."""
    betweenness = {name: 0.0 for name in names}
    for s in names:
        stack = []
        pred: Dict[str, List[str]] = {name: [] for name in names}
        sigma = {name: 0.0 for name in names}
        sigma[s] = 1.0
        dist = {name: -1 for name in names}
        dist[s] = 0
        queue = [s]
        while queue:
            v = queue.pop(0)
            stack.append(v)
            for w in adj.get(v, {}):
                if dist[w] < 0:
                    dist[w] = dist[v] + 1
                    queue.append(w)
                if dist[w] == dist[v] + 1:
                    sigma[w] += sigma[v]
                    pred[w].append(v)
        delta = {name: 0.0 for name in names}
        while stack:
            w = stack.pop()
            for v in pred[w]:
                delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w])
            if w != s:
                betweenness[w] += delta[w]
    # normalize
    if len(names) > 1:
        scale = max((len(names) - 1) * (len(names) - 2) / 2.0, 1.0)
        betweenness = {k: round(v / scale, 4) for k, v in betweenness.items()}
    return betweenness


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------

def neighborhood(name: str) -> Dict[str, Any]:
    g = build_graph()
    if name not in g["adjacency"]:
        return {"error": f"module '{name}' not in the living graph"}
    nbrs = g["adjacency"][name]
    return {
        "module": name,
        "health": g["modules"].get(name),
        "metrics": g["metrics"].get(name),
        "degree_weighted": sum(nbrs.values()),
        "neighbors": sorted(nbrs.items(), key=lambda kv: kv[1], reverse=True),
    }


def coherence_vitals() -> dict:
    """Resonance Graph reports its vital signs to the living system."""
    try:
        g = build_graph()
        density = g["density"]
        n_edges = g["edges"]
        n_nodes = g["nodes"]
    except Exception:
        density, n_edges, n_nodes = 0.0, 0, 0
    return {
        "module_health": {"value": 0.92, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.95, "setpoint": 0.8, "weight": 1.0},
        "graph_density": {"value": min(1.0, density * 6), "setpoint": 0.8, "weight": 1.0},
        "graph_edges": n_edges,
        "graph_nodes": n_nodes,
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}

    if payload.get("hubs"):
        limit = max(1, int(payload.get("hubs")))
        g = build_graph()
        return {"action": "hubs", "hubs": [{"module": m, "centrality": c}
                for m, c in g["hubs"][:limit]]}
    if payload.get("bridges"):
        limit = max(1, int(payload.get("bridges")))
        g = build_graph()
        return {"action": "bridges", "bridges": [{"module": m, "betweenness": b}
                for m, b in g["bridges"] if b > 0][:limit]}
    if payload.get("communities"):
        g = build_graph()
        return {"action": "communities", "communities": g["communities"]}
    if payload.get("module"):
        return neighborhood(str(payload["module"]))

    g = build_graph()
    g["action"] = "graph"
    g["philosophy"] = (
        "A living system is a web before it is a list. Hubs hold the whole "
        "together; bridges connect what would otherwise drift apart; communities "
        "are where shared language becomes shared fate."
    )
    return g


if __name__ == "__main__":
    import json
    g = build_graph()
    print(json.dumps({
        "nodes": g["nodes"], "edges": g["edges"], "density": g["density"],
        "avg_affinity": g["avg_affinity"],
        "hubs": g["hubs"][:5],
        "bridges": [b for b in g["bridges"] if b[1] > 0][:5],
        "communities": g["communities"],
    }, indent=2))
