"""Gossip Uptime — how fast does information spread through the frontier?

Extension of gossip_network: simulates how fast a rumor from module A
reaches the whole constellation. The "uptime" is the average hop count
for a rumor to reach 50% of the network — a measure of how tightly
coupled the frontier is.

A lower uptime means modules are well-connected (information flows fast).
A higher uptime means modules are isolated (information diffuses slowly).
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, List, Set

ROOT = Path(__file__).resolve().parents[1]


def _module_graph() -> Dict[str, List[str]]:
    """Build a weighted adjacency graph from module co-name words.

    Two modules are connected if they share root word tokens; the more
    tokens they share, the more strongly they gossip (we model this by
    listing each neighbor once per shared token, so `dream_synthesis`
    and `dream_architect` have 2 links, not 1).
    """
    import re
    api_dir = ROOT / "api"
    names = [p.stem for p in api_dir.glob("*.py")
             if p.stem not in ("__init__", "index")]
    tokens: Dict[str, Set[str]] = {}
    for name in names:
        for tok in re.findall(r"[a-z]+", name.lower()):
            tokens.setdefault(tok, set()).add(name)
    adj: Dict[str, List[str]] = {n: [] for n in names}
    for tok, members in tokens.items():
        members = list(members)
        for i, a in enumerate(members):
            for b in members[i + 1:]:
                adj[a].append(b)
                adj[b].append(a)
    return adj


def simulate(origin: str, target_pct: float = 0.5, hops: int = 8) -> Dict[str, Any]:
    """Simulate gossip propagation from an origin module.

    At each hop the rumor spreads to each neighbor with probability p
    proportional to the number of shared words (dense = more likely).
    We track how many modules heard it after each hop.
    """
    graph = _module_graph()
    if origin not in graph:
        return {"error": f"unknown module: {origin}", "origin": origin}

    total = len(graph)
    heard = {origin}
    frontier = {origin}
    trajectory = [len(heard)]

    for h in range(1, hops + 1):
        next_frontier = set()
        for node in frontier:
            for neighbor in graph.get(node, []):
                if neighbor not in heard:
                    # each shared word is a channel => strong families spread fast
                    if hash(f"{node}:{neighbor}:{h}") % 1000 / 1000.0 < 0.85:
                        next_frontier.add(neighbor)
                        heard.add(neighbor)
        frontier = next_frontier
        trajectory.append(len(heard))
        if len(heard) >= total * target_pct:
            break

    pct = round(len(heard) / total * 100, 1) if total else 0
    uptime_hop = next((i for i, c in enumerate(trajectory) if c >= total * target_pct), hops)

    return {
        "module": "gossip_uptime",
        "prophecy": "fulfilled",
        "origin": origin,
        "total_modules": total,
        "reached_pct": pct,
        "uptime_hops": uptime_hop,
        "target_pct": int(target_pct * 100),
        "trajectory": trajectory,
        "note": "gossip propagates through co-name-word adjacency",
    }


def handler(payload: dict = None, context: object = None) -> dict:
    origin = (payload or {}).get("origin", "gossip_network")
    return simulate(origin)


if __name__ == "__main__":
    import json
    r = simulate("gossip_network")
    print(json.dumps(r, indent=2))

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "interface", "status": "active", "wave": "0", "module": "gossip_uptime"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
