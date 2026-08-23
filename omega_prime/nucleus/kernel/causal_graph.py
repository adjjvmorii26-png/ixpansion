"""Causal echo graph.

Every action-effect pair is recorded as a directed edge in a DAG.
When an agent observes an unexpected outcome, it can trace backward
through the causal chain to discover which prior actions contributed
to the current state. This enables post-hoc reasoning about why
things went wrong.
"""
from __future__ import annotations

import hashlib
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CausalNode:
    node_id: str
    tick: int
    actor: str
    action_type: str
    payload_hash: str
    effect_observed: str | None = None
    is_anomaly: bool = False


class CausalGraph:
    def __init__(self, max_depth: int = 64) -> None:
        self._nodes: dict[str, CausalNode] = {}
        self._edges: dict[str, list[str]] = defaultdict(list)  # cause_id -> [effect_ids]
        self._reverse: dict[str, list[str]] = defaultdict(list)  # effect_id -> [cause_ids]
        self.max_depth = max_depth

    def _make_id(self, actor: str, action_type: str, tick: int) -> str:
        raw = f"{actor}:{action_type}:{tick}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def record_action(self, actor: str, action_type: str, tick: int,
                      causes: list[str] | None = None) -> str:
        """Record an action. Optionally link to known causal predecessors."""
        nid = self._make_id(actor, action_type, tick)
        node = CausalNode(node_id=nid, tick=tick, actor=actor,
                          action_type=action_type,
                          payload_hash=hashlib.md5(f"{actor}{action_type}".encode()).hexdigest()[:8])
        self._nodes[nid] = node

        if causes:
            for cid in causes:
                if cid in self._nodes:
                    self._edges[cid].append(nid)
                    self._reverse[nid].append(cid)
        return nid

    def record_effect(self, node_id: str, effect: str, is_anomaly: bool = False) -> None:
        """Attach an observed effect to a previously recorded action."""
        if node_id in self._nodes:
            self._nodes[node_id].effect_observed = effect
            self._nodes[node_id].is_anomaly = is_anomaly

    def trace_root_causes(self, node_id: str, max_depth: int | None = None) -> list[CausalNode]:
        """BFS backwards from a node to find all causal ancestors."""
        depth_limit = max_depth or self.max_depth
        visited: set[str] = set()
        queue: deque[tuple[str, int]] = deque([(node_id, 0)])
        ancestors: list[CausalNode] = []

        while queue:
            current, d = queue.popleft()
            if current in visited or d >= depth_limit:
                continue
            visited.add(current)
            for parent in self._reverse.get(current, []):
                if parent not in visited:
                    ancestors.append(self._nodes[parent])
                    queue.append((parent, d + 1))

        return sorted(ancestors, key=lambda n: n.tick)

    def find_anomaly_sources(self) -> list[CausalNode]:
        """Return all nodes flagged as anomalies with their root-cause chains."""
        anomalies = [n for n in self._nodes.values() if n.is_anomaly]
        return anomalies

    @property
    def stats(self) -> dict[str, Any]:
        total_edges = sum(len(v) for v in self._edges.values())
        return {
            "nodes": len(self._nodes),
            "edges": total_edges,
            "anomalies": len([n for n in self._nodes.values() if n.is_anomaly]),
            "actors": len(set(n.actor for n in self._nodes.values())),
        }
