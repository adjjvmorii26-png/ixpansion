#!/usr/bin/env python3
"""Layout agents as a constellation graph from stable HEX sigils."""
from __future__ import annotations
import hashlib, json, math
from pathlib import Path

OUT = Path(__file__).resolve().parent / "constellation.json"
AGENTS = ["forge_mind", "wanderer", "archivist", "sentinel", "mimic", "pulse_driver"]

def sigil(name: str) -> str:
    return "0x" + hashlib.sha256(name.encode()).hexdigest()[:8].upper()

def layout() -> dict:
    nodes = []
    n = len(AGENTS)
    for i, name in enumerate(AGENTS):
        s = sigil(name)
        angle = 2 * math.pi * i / n
        nodes.append({"id": name, "sigil": s, "x": round(math.cos(angle), 4),
                      "y": round(math.sin(angle), 4), "hue": f"#{s[2:8]}"})
    edges = [{"from": AGENTS[i], "to": AGENTS[(i + 1) % n]} for i in range(n)]
    edges.append({"from": "pulse_driver", "to": "sentinel"})
    graph = {"type": "sigil_constellation", "nodes": nodes, "edges": edges}
    OUT.write_text(json.dumps(graph, indent=2) + "\n")
    return graph

if __name__ == "__main__":
    print(json.dumps(layout(), indent=2))
