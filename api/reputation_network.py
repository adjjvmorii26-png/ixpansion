"""Reputation Network — agents earn, lose, and transfer trust through interactions.

Trust is not binary — it's a continuous, transitive quantity. If A trusts B
and B trusts C, A has partial trust in C. The network computes transitive
trust, detects trust clusters, and identifies trusted isolates.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class TrustEdge:
    def __init__(self, source: str, target: str, trust: float = 0.5):
        self.source = source
        self.target = target
        self.trust = min(max(trust, 0.0), 1.0)
        self.interactions = 0
        self.created_at = time.time()

    def interact(self, positive: bool):
        self.interactions += 1
        if positive:
            self.trust = min(1.0, self.trust + 0.05)
        else:
            self.trust = max(0.0, self.trust - 0.1)


class ReputationNetwork:
    def __init__(self):
        self.edges: Dict[str, TrustEdge] = {}
        self.agents: Set[str] = set()

    def _edge_key(self, source: str, target: str) -> str:
        return f"{source}->{target}"

    def register(self, agent_id: str) -> Dict[str, Any]:
        self.agents.add(agent_id)
        return {"registered": agent_id}

    def trust(self, source: str, target: str, amount: float = 0.5) -> Dict[str, Any]:
        key = self._edge_key(source, target)
        if key in self.edges:
            self.edges[key].trust = min(max(amount, 0.0), 1.0)
        else:
            self.edges[key] = TrustEdge(source, target, amount)
        self.agents.add(source)
        self.agents.add(target)
        return {"source": source, "target": target, "trust": round(amount, 4)}

    def interact(self, source: str, target: str, positive: bool = True) -> Dict[str, Any]:
        key = self._edge_key(source, target)
        if key not in self.edges:
            self.edges[key] = TrustEdge(source, target, 0.5)
        self.edges[key].interact(positive)
        return {
            "source": source,
            "target": target,
            "positive": positive,
            "trust": round(self.edges[key].trust, 4),
        }

    def transitive_trust(self, source: str, target: str, depth: int = 3) -> float:
        """Compute trust from source to target through the network."""
        if source == target:
            return 1.0
        visited = {source}
        queue = [(source, 1.0)]
        max_trust = 0.0
        for _ in range(depth):
            next_queue = []
            for node, trust_so_far in queue:
                for key, edge in self.edges.items():
                    if edge.source == node and edge.target not in visited:
                        transitive = trust_so_far * edge.trust
                        if edge.target == target:
                            max_trust = max(max_trust, transitive)
                        visited.add(edge.target)
                        next_queue.append((edge.target, transitive))
            queue = next_queue
        return max_trust

    def trust_clusters(self) -> List[List[str]]:
        """Find clusters of mutually trusting agents."""
        adj: Dict[str, List[str]] = {}
        for edge in self.edges.values():
            if edge.trust > 0.7:
                adj.setdefault(edge.source, []).append(edge.target)
                adj.setdefault(edge.target, []).append(edge.source)
        visited: Set[str] = set()
        clusters = []
        for agent in self.agents:
            if agent in visited:
                continue
            cluster = set()
            stack = [agent]
            while stack:
                current = stack.pop()
                if current in visited:
                    continue
                visited.add(current)
                cluster.add(current)
                for neighbor in adj.get(current, []):
                    if neighbor not in visited:
                        stack.append(neighbor)
            if len(cluster) >= 2:
                clusters.append(sorted(cluster))
        return clusters

    def trusted_isolates(self) -> List[Dict[str, Any]]:
        """Agents who give trust to nobody and receive none."""
        gives = set(e.source for e in self.edges.values())
        receives = set(e.target for e in self.edges.values())
        isolates = []
        for agent in self.agents:
            if agent not in gives and agent not in receives:
                isolates.append({"agent": agent, "status": "isolated"})
        return isolates

    def network_stats(self) -> Dict[str, Any]:
        avg_trust = sum(e.trust for e in self.edges.values()) / max(len(self.edges), 1)
        return {
            "total_agents": len(self.agents),
            "total_edges": len(self.edges),
            "average_trust": round(avg_trust, 4),
            "clusters": len(self.trust_clusters()),
            "isolates": len(self.trusted_isolates()),
        }


_network = ReputationNetwork()


def reputation_network_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "register":
        return _network.register(payload.get("agent_id", f"agent_{random.randint(1000,9999)}"))
    elif action == "trust":
        return _network.trust(
            payload.get("source", ""), payload.get("target", ""),
            payload.get("amount", 0.5),
        )
    elif action == "interact":
        return _network.interact(
            payload.get("source", ""), payload.get("target", ""),
            payload.get("positive", True),
        )
    elif action == "transitive":
        return {
            "source": payload.get("source", ""),
            "target": payload.get("target", ""),
            "transitive_trust": round(
                _network.transitive_trust(
                    payload.get("source", ""),
                    payload.get("target", ""),
                    payload.get("depth", 3),
                ), 4
            ),
        }
    elif action == "clusters":
        return {"clusters": _network.trust_clusters()}
    elif action == "isolates":
        return {"isolates": _network.trusted_isolates()}
    return {"status": "active", **_network.network_stats()}


handler = reputation_network_handler

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "agent", "status": "active", "wave": "0", "module": "reputation_network"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/status")
    if path == "/status":
        return {"action": "status", "module": "reputation_network", "status": "active"}
    return {"error": "unknown", "available": ["/status"]}
