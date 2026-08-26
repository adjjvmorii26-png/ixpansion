"""Temporal Collapse Engine — compress time, replay futures, and branch causality.

Agents can compress hours of simulation into seconds, replay failed futures
to find alternatives, and branch causality trees to explore counterfactuals.
"""
from __future__ import annotations

import hashlib
import json
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class TemporalNode:
    """A point in the causal tree."""

    def __init__(self, event: str, timestamp: float, parent: Optional[str] = None):
        self.event = event
        self.timestamp = timestamp
        self.parent = parent
        self.children: List[str] = []
        self.hash = hashlib.sha256(f"{event}:{timestamp}".encode()).hexdigest()[:12]


class TemporalCollapseEngine:
    """Compresses time, replays futures, branches causality."""

    def __init__(self):
        self.tree: Dict[str, TemporalNode] = {}
        self.collapsed: Dict[str, Any] = {}
        self.branches: Dict[str, List[str]] = {}
        self._origin = TemporalNode("origin", time.time())
        self.tree[self._origin.hash] = self._origin

    def add_event(self, event: str, parent_hash: Optional[str] = None) -> str:
        """Record an event in the causal tree."""
        parent = parent_hash or self._origin.hash
        node = TemporalNode(event, time.time(), parent)
        self.tree[node.hash] = node
        if parent in self.tree:
            self.tree[parent].children.append(node.hash)
        return node.hash

    def collapse(self, branch_id: str, depth: int = 5) -> Dict[str, Any]:
        """Collapse a branch into a compressed summary."""
        if branch_id not in self.tree:
            return {"error": "branch not found"}
        node = self.tree[branch_id]
        events = [node.event]
        current = node
        for _ in range(depth):
            if current.children:
                child_id = random.choice(current.children)
                current = self.tree[child_id]
                events.append(current.event)
        compressed = {
            "branch": branch_id,
            "events_collapsed": len(events),
            "timeline": events,
            "entropy": random.random(),
            "compressed_at": time.time(),
        }
        self.collapsed[branch_id] = compressed
        return compressed

    def branch_causality(self, from_hash: str, alt_event: str) -> str:
        """Create an alternative future from a point in time."""
        if from_hash not in self.tree:
            return ""
        alt_node = TemporalNode(alt_event, time.time(), from_hash)
        self.tree[alt_node.hash] = alt_node
        self.tree[from_hash].children.append(alt_node.hash)
        if from_hash not in self.branches:
            self.branches[from_hash] = []
        self.branches[from_hash].append(alt_node.hash)
        return alt_node.hash

    def replay_future(self, branch_id: str, steps: int = 10) -> List[str]:
        """Replay possible futures from a branch point."""
        if branch_id not in self.tree:
            return []
        path = [branch_id]
        current = branch_id
        for _ in range(steps):
            node = self.tree.get(current)
            if not node or not node.children:
                break
            current = random.choice(node.children)
            path.append(current)
        return [self.tree[h].event for h in path if h in self.tree]

    def timeline_stats(self) -> Dict[str, Any]:
        """Get statistics about the causal tree."""
        return {
            "total_nodes": len(self.tree),
            "total_branches": len(self.branches),
            "total_collapsed": len(self.collapsed),
            "max_depth": max(
                (self._depth(h) for h in self.tree), default=0
            ),
        }

    def _depth(self, node_hash: str, visited: Optional[set] = None) -> int:
        if visited is None:
            visited = set()
        if node_hash in visited or node_hash not in self.tree:
            return 0
        visited.add(node_hash)
        node = self.tree[node_hash]
        if not node.children:
            return 1
        return 1 + max(self._depth(c, visited) for c in node.children)


# Singleton for API use
_engine = TemporalCollapseEngine()


def temporal_collapse_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle temporal collapse API requests."""
    action = payload.get("action", "status")

    if action == "add_event":
        event = payload.get("event", "unnamed_event")
        parent = payload.get("parent")
        node_id = _engine.add_event(event, parent)
        return {"status": "recorded", "node_id": node_id, "event": event}

    elif action == "collapse":
        branch = payload.get("branch", _engine._origin.hash)
        depth = payload.get("depth", 5)
        return _engine.collapse(branch, depth)

    elif action == "branch":
        from_point = payload.get("from", _engine._origin.hash)
        alt_event = payload.get("alt_event", "divergence")
        new_id = _engine.branch_causality(from_point, alt_event)
        return {"status": "branched", "new_branch": new_id}

    elif action == "replay":
        branch = payload.get("branch", _engine._origin.hash)
        steps = payload.get("steps", 10)
        future = _engine.replay_future(branch, steps)
        return {"replayed": future, "length": len(future)}

    return {"status": "active", **_engine.timeline_stats()}
