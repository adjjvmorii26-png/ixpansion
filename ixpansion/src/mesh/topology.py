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

def build_agent_mesh(strategy: str, agents: list[str]) -> list[tuple[str, str, str]]:
    """Build a communication graph where every named agent can transmit."""
    if strategy not in {"star", "ring", "chaotic"}:
        raise ValueError(f"unknown topology: {strategy}")
    if not agents:
        return []
    hub = "origin"
    if strategy == "star":
        edges: list[tuple[str, str, str]] = []
        for agent in agents:
            edges.append((agent, hub, "uplink"))
            edges.append((hub, agent, "downlink"))
        return edges
    nodes = [hub, *agents]
    if strategy == "ring":
        return [
            (nodes[index], nodes[(index + 1) % len(nodes)], "ring")
            for index in range(len(nodes))
        ]
    return [
        (source, target, "chaotic")
        for index, source in enumerate(nodes)
        for target in nodes[index + 1:]
    ] + [
        (target, source, "chaotic")
        for index, source in enumerate(nodes)
        for target in nodes[index + 1:]
    ]
