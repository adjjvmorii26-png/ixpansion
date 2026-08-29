"""Prophecy Network — predictions that influence each other and create feedback loops.

Prophecies don't exist in isolation. When one prophecy references another,
they form a network of interconnected predictions. Prophecies can reinforce
each other, contradict each other, or create cascading prediction chains
where one fulfilled prophecy triggers the next.
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


class ProphecyNode:
    def __init__(self, text: str, author: str, confidence: float = 0.5):
        self.text = text
        self.author = author
        self.confidence = min(max(confidence, 0.0), 1.0)
        self.dependencies: List[str] = []
        self.dependents: List[str] = []
        self.fulfilled = None
        self.timestamp = time.time()
        self.id = hashlib.sha256(f"{text}:{self.timestamp}".encode()).hexdigest()[:8]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text[:80],
            "author": self.author,
            "confidence": round(self.confidence, 3),
            "dependencies": len(self.dependencies),
            "dependents": len(self.dependents),
            "fulfilled": self.fulfilled,
        }


class ProphecyNetwork:
    def __init__(self):
        self.prophecies: Dict[str, ProphecyNode] = {}
        self.fulfillment_chain: List[Dict[str, Any]] = []

    def add_prophecy(self, text: str, author: str = "oracle", confidence: float = 0.5) -> Dict[str, Any]:
        node = ProphecyNode(text, author, confidence)
        self.prophecies[node.id] = node
        return {"prophecy": node.to_dict()}

    def link(self, source_id: str, target_id: str) -> Dict[str, Any]:
        if source_id not in self.prophecies or target_id not in self.prophecies:
            return {"error": "prophecy not found"}
        self.prophecies[source_id].dependents.append(target_id)
        self.prophecies[target_id].dependencies.append(source_id)
        return {"linked": f"{source_id} → {target_id}"}

    def fulfill(self, prophecy_id: str, outcome: str = "fulfilled") -> Dict[str, Any]:
        if prophecy_id not in self.prophecies:
            return {"error": "prophecy not found"}
        node = self.prophecies[prophecy_id]
        node.fulfilled = outcome
        cascade = []
        for dep_id in node.dependents:
            dep = self.prophecies[dep_id]
            unmet = [d for d in dep.dependencies if self.prophecies[d].fulfilled is None]
            if not unmet:
                dep.confidence *= 1.5
                dep.confidence = min(1.0, dep.confidence)
                cascade.append(dep_id)
        self.fulfillment_chain.append({
            "prophecy": prophecy_id, "outcome": outcome,
            "cascade": cascade, "time": time.time(),
        })
        return {"fulfilled": outcome, "cascade_size": len(cascade)}

    def active_prophecies(self) -> List[Dict[str, Any]]:
        return [p.to_dict() for p in self.prophecies.values() if p.fulfilled is None]

    def prophecy_graph(self) -> Dict[str, Any]:
        edges = []
        for pid, node in self.prophecies.items():
            for dep in node.dependents:
                edges.append({"from": pid, "to": dep})
        return {
            "nodes": len(self.prophecies),
            "edges": len(edges),
            "fulfilled": sum(1 for p in self.prophecies.values() if p.fulfilled is not None),
        }

    def network_stats(self) -> Dict[str, Any]:
        return {
            "total_prophecies": len(self.prophecies),
            "fulfilled": sum(1 for p in self.prophecies.values() if p.fulfilled is not None),
            "total_links": sum(len(p.dependencies) for p in self.prophecies.values()),
            "total_cascades": len(self.fulfillment_chain),
        }


_network = ProphecyNetwork()


def prophecy_network_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "add":
        return _network.add_prophecy(
            payload.get("text", "something will happen"),
            payload.get("author", "oracle"),
            payload.get("confidence", 0.5),
        )
    elif action == "link":
        return _network.link(payload.get("source_id", ""), payload.get("target_id", ""))
    elif action == "fulfill":
        return _network.fulfill(payload.get("prophecy_id", ""), payload.get("outcome", "fulfilled"))
    elif action == "active":
        return {"prophecies": _network.active_prophecies()}
    elif action == "graph":
        return _network.prophecy_graph()
    return {"status": "active", **_network.network_stats()}


handler = prophecy_network_handler
