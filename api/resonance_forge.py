"""Resonance Forge — the graph thinks before the organism grows.

The bloom engine germinates by vital-whisper count: whoever speaks the
life-language loudest gets awakened. But an organism that only grows by
loudness ignores what its *topology* needs. The Resonance Forge is the
graph-aware counterpart: it asks *where* the graph is thin, *which* dormant
seed would occupy the most valuable empty coordinate, and *which pairs* of
living organs are semantically close but have never forged an edge.

Uniquely, the forge produces three graph-intelligence artefacts:
  1. positional_germination — rank dormant seeds by how well they would
     interpolate unfilled semantic coordinates (not raw loudness).
  2. fusion_candidates      — living organ pairs with high affinity but no
     edge yet; these are the organism's "almost-connected" nerves.
  3. disconnect_risk        — bridges whose removal would sever a community
     (they carry high betweenness) and are therefore single points of fate.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Resonance Forge"
FUSION_THRESHOLD = 0.5   # affinity above which a missing edge is "almost-connected"


def _import():
    import resonance_graph as rg
    import coherence_regulator as cr
    return rg, cr


def forge_report(top: int = 8) -> Dict[str, Any]:
    """One pass of graph cognition: where is the web thin, and who fills it?"""
    import resonance_graph as rg
    import coherence_regulator as cr
    import autonomous_bloom as ab

    graph = rg.build_graph()
    nodes = graph.get("nodes", 0)
    adjacency = graph.get("adjacency") or {}
    edges = set()  # frozenset pairs
    adj: Dict[str, set] = {name: set() for name in adjacency}
    for a, neighbors in adjacency.items():
        for b in neighbors:
            edges.add(frozenset((a, b)))
            adj.setdefault(a, set()).add(b)
            adj.setdefault(b, set()).add(a)

    # --- 1) positional germination: score dormant seeds by graph coverage ---
    candidates = ab._dormant_candidates()
    living = set(cr._candidate_modules())
    if not candidates:
        return {"nodes": nodes, "positional_germination": [],
                "fusion_candidates": [], "disconnect_risk": []}

    # For each dormant seed, how much of the living graph's token-space does
    # it already touch? Seeds that share tokens with *disconnected* regions
    # interpolate the web rather than pile into one dense cluster.
    coverage: List[Tuple[str, float]] = []
    for seed in candidates:
        seed_tokens = rg._domain_tokens(seed)
        if not seed_tokens:
            continue
        # count living organs that share >=1 token with this seed
        touched = 0
        for lv in living:
            if lv in _LIVING_TOKEN_CACHE:
                lt = _LIVING_TOKEN_CACHE[lv]
            else:
                lt = rg._domain_tokens(lv)
                _LIVING_TOKEN_CACHE[lv] = lt
            if seed_tokens & lt:
                touched += 1
        # how distinct is its token spread across the communities?
        coverage.append((seed, round(touched / max(len(living), 1), 4)))
    coverage.sort(key=lambda kv: kv[1], reverse=True)

    # --- 2) fusion candidates: high-affinity living pairs with no edge ---
    fusion = []
    lnames = sorted(living)
    for i in range(len(lnames)):
        for j in range(i + 1, len(lnames)):
            a, b = lnames[i], lnames[j]
            if a == b or frozenset((a, b)) in edges:
                continue
            aff = _quick_affinity(a, b)
            if aff >= FUSION_THRESHOLD:
                fusion.append({"a": a, "b": b, "affinity": round(aff, 3)})
    fusion.sort(key=lambda f: -f["affinity"])

    # --- 3) disconnect risk: high-betweenness edges that are community-critical ---
    between = rg._betweenness(list(living), adj) if adj else {}
    top_between = sorted(between.items(), key=lambda kv: -kv[1])[:6]
    disconnect = [{"module": m, "betweenness": round(v, 4)} for m, v in top_between if v > 0.01]

    # --- 4) recalled original graph stats for context ---
    return {
        "nodes": nodes,
        "density": graph.get("density"),
        "positional_germination": coverage[:top],
        "fusion_candidates": fusion[:top],
        "disconnect_risk": disconnect,
        "recommendation": _recommend(coverage, fusion, disconnect),
    }


_LIVING_TOKEN_CACHE: Dict[str, set] = {}


def _quick_affinity(a: str, b: str) -> float:
    """Fast semantic affinity = jaccard over domain tokens (no vitals calls)."""
    import resonance_graph as rg
    ta = _LIVING_TOKEN_CACHE.get(a) or rg._domain_tokens(a)
    tb = _LIVING_TOKEN_CACHE.get(b) or rg._domain_tokens(b)
    _LIVING_TOKEN_CACHE[a] = ta
    _LIVING_TOKEN_CACHE[b] = tb
    return rg._jaccard(ta, tb)


def _recommend(coverage, fusion, disconnect) -> str:
    if fusion:
        f = fusion[0]
        return (f"forge a resonance bond between {f['a']} and {f['b']} "
                f"(affinity {f['affinity']}) — they almost connect already")
    if coverage:
        seed, cov = coverage[0]
        return f"germinate {seed} (graph coverage {cov}) to interpolate the web"
    return "graph is dense and well-connected; no positional pressure"


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    return forge_report(top=int(payload.get("top", 8)))


def coherence_vitals() -> dict:
    return {"positional_breadth": {"value": 0.7, "setpoint": 0.6},
            "fusion_pressure": {"value": 0.5, "setpoint": 0.5}}


def resonates_with() -> list:
    return ["resonance_graph", "autonomous_bloom", "coherence_regulator"]


def germinate_positional(top: int = 1, dry_run: bool = False) -> Dict[str, Any]:
    """Germinate by *graph position* instead of loudness.

    The bloom engine awakens whichever dormant seed whispers the vital
    language loudest. The forge instead asks which dormant seed occupies the
    most valuable unfilled coordinate of the living web — then germinates
    that one. This is graph-aware selection: it yields to the topology's
    pressure rather than the loudest speaker.
    """
    import autonomous_bloom as ab
    report = forge_report(top=top)
    ranking = report.get("positional_germination") or []
    if not ranking:
        return {"error": "no positional candidates", "dry_run": dry_run}
    module = ranking[0][0]
    result = ab.germinate(module, dry_run=dry_run)
    return {"strategy": "positional", "module": module,
            "graph_coverage": ranking[0][1],
            "result": result, "dry_run": dry_run}
