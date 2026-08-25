from __future__ import annotations
"""System Metabolism v2 — tracks energy flow through the entire codebase.

Like biological metabolism that converts food into energy, the codebase
has a metabolism: commits are "food," CPU cycles are "energy," and
technical debt is "waste." This v2 tracks the full metabolic cycle
across all subsystems with flow analysis.
"""
import math
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

@dataclass
class MetabolicNode:
    name: str
    input_energy: float = 0.0
    output_energy: float = 0.0
    waste: float = 0.0
    efficiency: float = 0.0

class SystemMetabolismV2:
    def __init__(self):
        self.nodes: Dict[str, MetabolicNode] = {}
        self.flows: List[Tuple[str, str, float]] = []
        self.tick = 0

    def register(self, name: str, input_energy: float = 0.0,
                 output_energy: float = 0.0, waste: float = 0.0):
        efficiency = output_energy / max(input_energy, 0.001)
        self.nodes[name] = MetabolicNode(
            name=name, input_energy=input_energy,
            output_energy=output_energy, waste=waste,
            efficiency=efficiency,
        )

    def flow(self, source: str, target: str, energy: float):
        self.flows.append((source, target, energy))
        if source in self.nodes:
            self.nodes[source].output_energy += energy
        if target in self.nodes:
            self.nodes[target].input_energy += energy

    def step(self):
        self.tick += 1
        for node in self.nodes.values():
            node.efficiency = node.output_energy / max(node.input_energy, 0.001)
            node.waste = max(0, node.input_energy - node.output_energy) * 0.1

    def metabolic_report(self) -> Dict:
        total_input = sum(n.input_energy for n in self.nodes.values())
        total_output = sum(n.output_energy for n in self.nodes.values())
        total_waste = sum(n.waste for n in self.nodes.values())
        return {
            "nodes": len(self.nodes),
            "flows": len(self.flows),
            "total_input": round(total_input, 2),
            "total_output": round(total_output, 2),
            "total_waste": round(total_waste, 2),
            "overall_efficiency": round(total_output / max(total_input, 0.001), 3),
            "node_details": [
                {"name": n.name, "efficiency": round(n.efficiency, 3),
                 "waste": round(n.waste, 2)}
                for n in sorted(self.nodes.values(),
                               key=lambda x: x.efficiency, reverse=True)
            ],
        }


def demo():
    meta = SystemMetabolismV2()
    print("=== System Metabolism v2 ===")
    meta.register("commits", input_energy=100)
    meta.register("build", input_energy=0)
    meta.register("tests", input_energy=0)
    meta.register("deploy", input_energy=0)
    meta.register("runtime", input_energy=0)
    meta.flow("commits", "build", 80)
    meta.flow("build", "tests", 70)
    meta.flow("tests", "deploy", 60)
    meta.flow("deploy", "runtime", 50)
    meta.step()
    report = meta.metabolic_report()
    print(f"  Nodes: {report['nodes']}, Flows: {report['flows']}")
    print(f"  Efficiency: {report['overall_efficiency']}")
    print(f"  Waste: {report['total_waste']}")
    for n in report["node_details"]:
        print(f"    {n['name']}: efficiency={n['efficiency']}, waste={n['waste']}")
    return report


if __name__ == "__main__":
    demo()
