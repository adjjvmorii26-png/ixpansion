from __future__ import annotations
"""Provenance Tracker — traces the full lineage of any data transformation.

Like the proof garden's Merkle trees, this tracks the complete lineage
of how data flows through the system — every transformation, merge,
and decision point. Enables full audit trails and causality analysis.
"""
import math
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

@dataclass
class ProvenanceNode:
    node_id: str
    data_hash: str
    transformation: str
    inputs: List[str]
    outputs: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: int = 0

class ProvenanceTracker:
    def __init__(self):
        self.nodes: Dict[str, ProvenanceNode] = {}
        self.tick = 0

    def _hash_data(self, data: Any) -> str:
        raw = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(raw).hexdigest()[:16]

    def record(self, transformation: str, inputs: List[Any] = None,
               output: Any = None, metadata: Dict = None) -> ProvenanceNode:
        self.tick += 1
        input_hashes = [self._hash_data(d) for d in (inputs or [])]
        output_hash = self._hash_data(output) if output is not None else "null"
        node = ProvenanceNode(
            node_id=f"prov_{self.tick:04d}",
            data_hash=output_hash,
            transformation=transformation,
            inputs=input_hashes,
            outputs=[output_hash],
            metadata=metadata or {},
            timestamp=self.tick,
        )
        self.nodes[node.node_id] = node
        return node

    def trace(self, node_id: str) -> List[Dict]:
        if node_id not in self.nodes:
            return []
        chain = []
        visited = set()
        stack = [node_id]
        while stack:
            nid = stack.pop()
            if nid in visited:
                continue
            visited.add(nid)
            if nid in self.nodes:
                node = self.nodes[nid]
                chain.append({
                    "node": node.node_id,
                    "transformation": node.transformation,
                    "hash": node.data_hash,
                    "timestamp": node.timestamp,
                })
                stack.extend(node.inputs)
        return list(reversed(chain))

    def full_graph(self) -> Dict:
        return {
            "total_nodes": len(self.nodes),
            "total_transformations": len(set(n.transformation for n in self.nodes.values())),
            "nodes": [
                {"id": n.node_id, "transformation": n.transformation,
                 "hash": n.data_hash, "inputs": len(n.inputs)}
                for n in self.nodes.values()
            ],
        }


def demo():
    tracker = ProvenanceTracker()
    print("=== Provenance Tracker ===")
    tracker.record("raw_input", output={"value": 42}, metadata={"source": "sensor"})
    tracker.record("transform", inputs=[{"value": 42}], output={"value": 84},
                   metadata={"operation": "double"})
    tracker.record("aggregate", inputs=[{"value": 84}, {"value": 10}],
                   output={"total": 94}, metadata={"operation": "sum"})
    tracker.record("filter", inputs=[{"total": 94}], output={"total": 94},
                   metadata={"threshold": 50})
    trace = tracker.trace("prov_0004")
    print(f"  Trace for prov_0004:")
    for t in trace:
        print(f"    {t['node']}: {t['transformation']} (hash={t['hash']})")
    graph = tracker.full_graph()
    print(f"\n  Total nodes: {graph['total_nodes']}")
    print(f"  Transformations: {graph['total_transformations']}")
    return graph


if __name__ == "__main__":
    demo()
