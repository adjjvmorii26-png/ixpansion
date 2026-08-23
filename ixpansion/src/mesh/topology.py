from __future__ import annotations


def build_topology(strategy: str, nodes: list[str]) -> list[tuple[str, str, str]]:
    if strategy not in {"star", "ring", "chaotic"}:
        raise ValueError(f"unknown topology: {strategy}")
    if len(nodes) < 2:
        return []
    edges: list[tuple[str, str, str]] = []
    if strategy == "star":
        edges.extend((nodes[0], node, "hub") for node in nodes[1:])
    elif strategy == "ring":
        edges.extend((nodes[index], nodes[(index + 1) % len(nodes)], "ring") for index in range(len(nodes)))
    else:
        edges.extend((source, target, "chaotic") for index, source in enumerate(nodes) for target in nodes[index + 1:])
    return edges
