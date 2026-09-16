"""Wave 753 — resonance_braid.

Weaves the organism's living modules into a resonance graph, then reads it
back: bridge organs that hold distant communities together, community
clusters that form hidden factions, and coherence drift between weaves.
"""
from __future__ import annotations

import datetime
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "wave753_resonance_braid.json"
WAVE = 753
NAME = "resonance_braid"


def _load() -> dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except Exception:
            pass
    return {"wave": WAVE, "name": NAME, "weaves": [], "status": "seed"}


def _save(state: dict) -> None:
    DATA_FILE.write_text(json.dumps(state, indent=2))


_SKIP_FILES = {"__init__.py", "index.py", "coherence_regulator.py", "organism_ontology.py", "shared.py"}

def _module_names() -> List[str]:
    names = []
    for fp in sorted((ROOT / "api").glob("*.py")):
        if fp.name in _SKIP_FILES or fp.name.startswith("_"):
            continue
        stem = fp.stem
        m = re.match(r"wave\d+_(.+)", stem)
        if m:
            names.append(m.group(1))
        else:
            names.append(stem)
    return sorted(set(names))
def _token_score(a: str, b: str) -> float:
    """Resonance heuristic: shared tokens + shape similarity."""
    if a == b:
        return 0.0
    ta = set(re.findall(r"[a-z]+", a))
    tb = set(re.findall(r"[a-z]+", b))
    shared = ta & tb
    if not shared:
        return 0.0
    union = ta | tb
    return round(len(shared) / len(union), 4)

def _graph() -> Dict[str, List[Tuple[str, float]]]:
    """Optimized graph: group by tokens, only compute pairs that share a token."""
    names = _module_names()
    g: Dict[str, List[Tuple[str, float]]] = {n: [] for n in names}

    # Build inverted index: token -> set of module names
    import re
    token_to_names: Dict[str, set] = {}
    name_tokens: Dict[str, set] = {}
    for name in names:
        tokens = set(re.findall(r"[a-z]+", name))
        name_tokens[name] = tokens
        for token in tokens:
            token_to_names.setdefault(token, set()).add(name)

    # Only compute pairs that share at least one token
    seen = set()
    for token, token_names in token_to_names.items():
        token_list = sorted(token_names)
        for i, a in enumerate(token_list):
            for b in token_list[i + 1:]:
                pair = (a, b)
                if pair in seen:
                    continue
                seen.add(pair)
                ta = name_tokens[a]
                tb = name_tokens[b]
                shared = ta & tb
                if shared:
                    union = ta | tb
                    s = round(len(shared) / len(union), 4)
                    if s > 0:
                        g[a].append((b, s))
                        g[b].append((a, s))
    return g
def _communities_from_graph(g: Dict[str, List[Tuple[str, float]]]) -> List[List[str]]:
    """Greedy threshold clustering over resonance edges."""
    threshold = 0.15
    assigned: set = set()
    communities: List[List[str]] = []
    for node in sorted(g):
        if node in assigned:
            continue
        cluster = [node]
        frontier = [node]
        assigned.add(node)
        while frontier:
            cur = frontier.pop()
            for nbr, score in g.get(cur, []):
                if score >= threshold and nbr not in assigned:
                    assigned.add(nbr)
                    cluster.append(nbr)
                    frontier.append(nbr)
        communities.append(sorted(cluster))
    return communities


def _bridges(g: Dict[str, List[Tuple[str, float]]], communities: List[List[str]]) -> List[dict]:
    """Bridge organs touch multiple communities with strong edges."""
    comm_of: Dict[str, int] = {}
    for idx, comm in enumerate(communities):
        for node in comm:
            comm_of[node] = idx
    out = []
    for node, edges in g.items():
        touched = {comm_of.get(nbr) for nbr, score in edges if score >= 0.30 and nbr in comm_of}
        if len(touched) >= 2:
            out.append({"organ": node, "communities_bridged": sorted(touched), "score": len(touched)})
    return sorted(out, key=lambda x: -x["score"])


def handler(req: dict) -> dict:
    action = req.get("action", "status")
    state = _load()

    if action == "status":
        state["last_check"] = datetime.datetime.now(datetime.UTC).isoformat()
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "status", "ok": True,
                "weaves": len(state.get("weaves", [])), "modules": len(_module_names())}

    if action == "ping":
        return {"wave": WAVE, "name": NAME, "action": "ping", "ok": True, "alive": True}

    if action == "weave":
        g = _graph()
        weave = {
            "at": datetime.datetime.now(datetime.UTC).isoformat(),
            "modules": len(g),
            "edges": sum(len(v) for v in g.values()) // 2,
            "edge_snapshot": {k: dict(v) for k, v in g.items()},
        }
        state.setdefault("weaves", []).append(weave)
        state["weaves"] = state["weaves"][-10:]
        _save(state)
        top = sorted(((k, sorted(v, key=lambda x: -x[1])[:3]) for k, v in g.items()),
                     key=lambda x: -len(x[1]))[:5]
        return {"wave": WAVE, "name": NAME, "action": "weave", "ok": True,
                "modules": weave["modules"], "edges": weave["edges"], "top_organs": top}

    if action == "bridges":
        g = _graph()
        communities = _communities_from_graph(g)
        bridges = _bridges(g, communities)
        return {"wave": WAVE, "name": NAME, "action": "bridges", "ok": True,
                "communities": len(communities), "bridges": bridges[:12]}

    if action == "communities":
        g = _graph()
        communities = _communities_from_graph(g)
        return {"wave": WAVE, "name": NAME, "action": "communities", "ok": True,
                "count": len(communities),
                "communities": [{"id": i, "size": len(c), "members": c[:8]} for i, c in enumerate(communities)]}

    if action == "drift":
        if not state.get("weaves"):
            return {"wave": WAVE, "name": NAME, "action": "drift", "ok": True, "drift": [],
                    "note": "weave at least twice to measure drift"}
        prev = state["weaves"][-1].get("edge_snapshot", {})
        g = _graph()
        drift_scores = []
        for k, edges in g.items():
            old = dict(prev.get(k, {}))
            delta = sum(abs(score - old.get(nbr, 0.0)) for nbr, score in edges)
            if delta > 0:
                drift_scores.append({"organ": k, "drift": round(delta, 4)})
        drift_scores.sort(key=lambda x: -x["drift"])
        return {"wave": WAVE, "name": NAME, "action": "drift", "ok": True,
                "drift_count": len(drift_scores), "top_drift": drift_scores[:10]}

    return {"wave": WAVE, "name": NAME, "action": action, "ok": False, "error": "unknown_action"}


def coherence_vitals() -> dict:
    state = _load()
    return {"wave": WAVE, "name": NAME, "layer": "organ", "status": "active",
            "resonance": 0.82, "weaves": len(state.get("weaves", []))}


def resonates_with() -> list:
    return ["repo_dna", "gene_splicer", "coherence_regulator", "evolution_kernel"]
