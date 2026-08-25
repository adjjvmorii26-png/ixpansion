from __future__ import annotations
"""Topological Insulator — protected information channels.

Creates robust information channels that only allow specific flows,
like topological insulators that conduct on surfaces but not in bulk.
Edge states carry protected information while the bulk remains insulating.
"""
import math
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

@dataclass
class Channel:
    channel_id: str
    source: str
    target: str
    bandwidth: float = 1.0
    protected: bool = False
    edge_state: bool = False
    messages: List[str] = field(default_factory=list)

@dataclass
class InsulatorNode:
    name: str
    is_bulk: bool = True
    is_edge: bool = False
    connections: List[str] = field(default_factory=list)
    blocked_count: int = 0
    passed_count: int = 0

class TopologicalInsulator:
    def __init__(self):
        self.nodes: Dict[str, InsulatorNode] = {}
        self.channels: Dict[str, Channel] = {}
        self.message_log: List[Dict] = []

    def add_node(self, name: str, is_edge: bool = False) -> InsulatorNode:
        node = InsulatorNode(name=name, is_bulk=not is_edge, is_edge=is_edge)
        self.nodes[name] = node
        return node

    def connect(self, source: str, target: str, protected: bool = False) -> Channel:
        channel_id = f"{source}->{target}"
        channel = Channel(
            channel_id=channel_id, source=source, target=target,
            protected=protected,
            edge_state=self.nodes[source].is_edge and self.nodes[target].is_edge,
        )
        self.channels[channel_id] = channel
        self.nodes[source].connections.append(target)
        return channel

    def send(self, source: str, target: str, message: str) -> bool:
        channel_id = f"{source}->{target}"
        if channel_id not in self.channels:
            return False
        channel = self.channels[channel_id]
        source_node = self.nodes[source]
        target_node = self.nodes[target]

        if source_node.is_bulk and not channel.edge_state:
            target_node.blocked_count += 1
            self.message_log.append({
                "source": source, "target": target, "message": message,
                "result": "blocked", "reason": "bulk_insulation"
            })
            return False

        channel.messages.append(message)
        source_node.passed_count += 1
        target_node.passed_count += 1
        self.message_log.append({
            "source": source, "target": target, "message": message,
            "result": "passed", "protected": channel.protected,
            "edge_state": channel.edge_state,
        })
        return True

    def topology_map(self) -> Dict:
        return {
            "nodes": len(self.nodes),
            "channels": len(self.channels),
            "edge_nodes": [n for n, node in self.nodes.items() if node.is_edge],
            "bulk_nodes": [n for n, node in self.nodes.items() if node.is_bulk],
            "protected_channels": sum(1 for c in self.channels.values() if c.protected),
            "edge_channels": sum(1 for c in self.channels.values() if c.edge_state),
        }

    def transmission_stats(self) -> Dict:
        passed = sum(1 for m in self.message_log if m["result"] == "passed")
        blocked = sum(1 for m in self.message_log if m["result"] == "blocked")
        return {
            "total_messages": len(self.message_log),
            "passed": passed,
            "blocked": blocked,
            "pass_rate": round(passed / max(len(self.message_log), 1), 3),
        }


def demo():
    ti = TopologicalInsulator()
    print("=== Topological Insulator ===")

    for name in ["bulk_a", "bulk_b", "bulk_c", "bulk_d"]:
        ti.add_node(name, is_edge=False)
    for name in ["edge_1", "edge_2", "edge_3", "edge_4"]:
        ti.add_node(name, is_edge=True)

    ti.connect("bulk_a", "bulk_b", protected=False)
    ti.connect("edge_1", "edge_2", protected=True)
    ti.connect("edge_2", "edge_3", protected=True)
    ti.connect("edge_3", "edge_4", protected=True)
    ti.connect("edge_4", "edge_1", protected=True)
    ti.connect("bulk_a", "edge_1", protected=False)

    messages = [
        ("bulk_a", "bulk_b", "secret_data"),
        ("edge_1", "edge_2", "protected_info"),
        ("edge_2", "edge_3", "edge_message"),
        ("bulk_b", "bulk_c", "blocked_data"),
        ("edge_3", "edge_4", "edge_flow"),
        ("edge_4", "edge_1", "circuit_complete"),
    ]
    for src, tgt, msg in messages:
        result = ti.send(src, tgt, msg)
        print(f"  {src} -> {tgt}: {'PASSED' if result else 'BLOCKED'}")

    topo = ti.topology_map()
    print(f"\nTopology: {topo['edge_nodes']} edge, {topo['bulk_nodes']} bulk")
    print(f"Protected channels: {topo['protected_channels']}")

    stats = ti.transmission_stats()
    print(f"Transmission: {stats['passed']}/{stats['total_messages']} "
          f"({stats['pass_rate']:.0%})")

    return {"topology": topo, "stats": stats}


if __name__ == "__main__":
    demo()
