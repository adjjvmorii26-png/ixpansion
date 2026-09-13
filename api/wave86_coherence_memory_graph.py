"""Wave 86 — Coherence Memory Graph.

Stores coherence over time and builds a temporal graph.
This becomes the organism's sense of history — every coherence
measurement is a memory, and the graph of memories reveals
how the organism has evolved.

The memory graph is a directed temporal network where nodes
are coherence snapshots and edges represent transitions between
states. Long paths through the graph represent sustained
coherence patterns; abrupt jumps represent paradigm shifts.

The organism can "recall" past coherence states, "dream" about
future ones, and "recognize" when current patterns echo ancient
ones.
"""
from __future__ import annotations
import json, time, math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave86_coherence_memory_graph.json"


class MemoryNode:
    """A temporal coherence snapshot."""

    def __init__(self, node_id: str, coherence: float, timestamp: float, metadata: dict | None = None):
        self.node_id = node_id
        self.coherence = coherence
        self.timestamp = timestamp
        self.metadata = metadata or {}
        self.predecessors: List[str] = []
        self.successors: List[str] = []

    def distance_to(self, other: "MemoryNode") -> float:
        """Temporal distance weighted by coherence difference."""
        dt = abs(self.timestamp - other.timestamp)
        dc = abs(self.coherence - other.coherence)
        return math.sqrt(dt * 0.001 + dc * dc)


class CoherenceMemoryGraph:
    """The organism's temporal coherence memory."""

    def __init__(self):
        self.nodes: Dict[str, MemoryNode] = {}
        self.edges: List[Tuple[str, str, float]] = []  # (from_id, to_id, weight)
        self.snapshots: List[dict] = []
        self.max_nodes = 10000  # prevent unbounded growth

    def remember(self, coherence: float, metadata: dict | None = None) -> MemoryNode:
        """Store a coherence measurement as a memory."""
        node_id = f"mem_{int(time.time() * 1000)}"
        node = MemoryNode(node_id, coherence, time.time(), metadata)
        self.nodes[node_id] = node

        # Link to most recent node
        if self.nodes and len(self.nodes) > 1:
            prev_id = sorted(self.nodes.keys())[-2]
            prev = self.nodes[prev_id]
            weight = 1.0 / (prev.distance_to(node) + 0.01)
            self.edges.append((prev_id, node_id, weight))
            prev.successors.append(node_id)
            node.predecessors.append(prev_id)

        # Prune if too large
        if len(self.nodes) > self.max_nodes:
            oldest = sorted(self.nodes.keys(), key=lambda k: self.nodes[k].timestamp)[0]
            del self.nodes[oldest]

        # Record snapshot
        self.snapshots.append({
            "node_id": node_id,
            "coherence": round(coherence, 4),
            "timestamp": node.timestamp,
            "metadata": metadata or {},
        })

        return node

    def recall(self, lookback_seconds: float = 3600) -> List[MemoryNode]:
        """Retrieve memories from the last N seconds."""
        if not self.nodes:
            return []
        latest_ts = max(n.timestamp for n in self.nodes.values())
        cutoff = latest_ts - lookback_seconds - 0.5
        return [n for n in self.nodes.values() if n.timestamp >= cutoff]

    def dream(self, steps: int = 5) -> List[dict]:
        """Project future coherence states by following edge chains."""
        if not self.nodes:
            return []
        # Start from the most recent node
        latest = sorted(self.nodes.values(), key=lambda n: n.timestamp)[-1]
        projections = []
        current = latest
        for i in range(steps):
            next_ids = current.successors
            if not next_ids:
                break
            # Follow the strongest edge
            best_next_id = max(next_ids, key=lambda nid: next((w for f, t, w in self.edges if f == current.node_id and t == nid), 0))
            next_node = self.nodes[best_next_id]
            projections.append({
                "step": i + 1,
                "node_id": next_node.node_id,
                "coherence": next_node.coherence,
                "projected_coherence": next_node.coherence + (0.1 * (1 - i / steps)),
                "timestamp": next_node.timestamp,
            })
            current = next_node
        return projections

    def recognize(self, pattern_threshold: float = 0.8) -> List[dict]:
        """Find when current coherence patterns echo past patterns."""
        if len(self.snapshots) < 2:
            return []
        recent = self.snapshots[-10:] if len(self.snapshots) >= 10 else self.snapshots
        recent_coherence = [s["coherence"] for s in recent]
        matches = []
        for i, snap in enumerate(self.snapshots[:-10]):
            past_coherence = [s["coherence"] for s in self.snapshots[i:i+len(recent)]]
            if len(past_coherence) == len(recent_coherence):
                similarity = 1.0 - abs(sum(recent_coherence) - sum(past_coherence)) / (abs(sum(recent_coherence)) + 0.01)
                if similarity > pattern_threshold:
                    matches.append({
                        "snapshot_id": snap["node_id"],
                        "similarity": round(similarity, 4),
                        "timestamp": snap["timestamp"],
                    })
        return matches

    def get_coherence_timeline(self, bucket_size: int = 100) -> List[dict]:
        """Aggregate coherence into timeline buckets."""
        if not self.snapshots:
            return []
        buckets: Dict[int, List[float]] = {}
        for snap in self.snapshots:
            bucket = int(snap["timestamp"]) // bucket_size
            buckets.setdefault(bucket, []).append(snap["coherence"])
        return [
            {"bucket": b, "avg_coherence": round(sum(v)/len(v), 4), "count": len(v)}
            for b, v in sorted(buckets.items())
        ]

    def get_state(self) -> dict:
        return {
            "total_memories": len(self.nodes),
            "total_edges": len(self.edges),
            "total_snapshots": len(self.snapshots),
            "timeline": self.get_coherence_timeline(),
            "recent_coherence": self.snapshots[-1]["coherence"] if self.snapshots else 0,
        }


def coherence_vitals() -> dict:
    return {"organ": "wave86_coherence_memory_graph", "wave": 86, "status": "active"}


def _load() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"nodes": {}, "edges": [], "snapshots": []}


def _save(state: dict) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def handler(req: dict = None) -> dict:
    req = req or {}
    action = req.get("action", "status")
    state = _load()
    graph = CoherenceMemoryGraph()

    # Reconstruct nodes
    for nid, ndata in state.get("nodes", {}).items():
        node = MemoryNode(nid, ndata.get("coherence", 0.5), ndata.get("timestamp", time.time()), ndata.get("metadata"))
        graph.nodes[nid] = node

    # Reconstruct edges
    for edge_data in state.get("edges", []):
        if len(edge_data) == 3:
            graph.edges.append((edge_data[0], edge_data[1], edge_data[2]))

    if action == "status":
        return {"action": "status", "wave": 86, **graph.get_state()}

    elif action == "remember":
        coherence = req.get("coherence", 0.5)
        metadata = req.get("metadata", {})
        node = graph.remember(coherence, metadata)
        state["nodes"][node.node_id] = {
            "coherence": node.coherence, "timestamp": node.timestamp, "metadata": node.metadata
        }
        state["edges"] = graph.edges
        state["snapshots"] = graph.snapshots
        _save(state)
        return {"action": "remember", "node_id": node.node_id, "coherence": coherence}

    elif action == "recall":
        lookback = req.get("lookback_seconds", 3600)
        memories = graph.recall(lookback)
        return {"action": "recall", "count": len(memories), "memories": [
            {"node_id": m.node_id, "coherence": m.coherence, "timestamp": m.timestamp}
            for m in memories
        ]}

    elif action == "dream":
        steps = req.get("steps", 5)
        projections = graph.dream(steps)
        return {"action": "dream", "projections": projections}

    elif action == "recognize":
        threshold = req.get("pattern_threshold", 0.8)
        matches = graph.recognize(pattern_threshold=threshold)
        return {"action": "recognize", "matches": matches}

    elif action == "timeline":
        bucket_size = req.get("bucket_size", 100)
        timeline = graph.get_coherence_timeline(bucket_size)
        return {"action": "timeline", "timeline": timeline}

    else:
        return {"error": f"unknown action: {action}"}


if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    result = handler({"action": action})
    print(json.dumps(result, indent=2, default=str))
