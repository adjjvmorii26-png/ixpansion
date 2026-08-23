from __future__ import annotations
from typing import Any

from core.state_graph import StateGraph


class ParadoxEngine:
    def scan(self, graph: StateGraph) -> dict[str, list[str]]:
        anomalies: dict[str, list[str]] = {"identity_split": [], "rule_collision": []}
        seen_kinds: set[str] = set()
        seen_ids: set[str] = set()
        for node in graph.nodes.values():
            if node.id in seen_ids:
                anomalies["identity_split"].append(node.id)
            seen_ids.add(node.id)
            signature = f"{node.kind}:{node.state.get('anomaly')}"
            if signature.endswith("identity-split"):
                anomalies["identity_split"].append(node.id)
            if node.kind in seen_kinds and node.kind != "region":
                anomalies["rule_collision"].append(node.id)
            seen_kinds.add(node.kind)
        return anomalies
