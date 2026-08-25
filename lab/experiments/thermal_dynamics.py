from __future__ import annotations
"""Thermal Dynamics — heat flow simulation through codebase topology.

Modules generate "heat" based on complexity and change frequency. Heat
flows between connected modules via conduction. Hotspots indicate
bottlenecks; cold zones indicate unused code. Thermal equilibrium is
the system's natural resting state.
"""
import math
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

@dataclass
class ThermalNode:
    name: str
    temperature: float = 20.0
    heat_capacity: float = 1.0
    thermal_conductivity: float = 0.1
    heat_generated: float = 0.0
    connections: List[str] = field(default_factory=list)

@dataclass
class ThermalReading:
    name: str
    temperature: float
    heat_generated: float
    neighbors: int
    thermal_flux: float

class ThermalDynamicsEngine:
    def __init__(self, ambient_temp: float = 20.0, cooling_rate: float = 0.01):
        self.ambient_temp = ambient_temp
        self.cooling_rate = cooling_rate
        self.nodes: Dict[str, ThermalNode] = {}
        self.time_step = 0
        self.temperature_history: Dict[str, List[float]] = {}

    def add_node(self, name: str, temperature: float = 20.0,
                 heat_capacity: float = 1.0, conductivity: float = 0.1) -> ThermalNode:
        node = ThermalNode(
            name=name, temperature=temperature,
            heat_capacity=heat_capacity, thermal_conductivity=conductivity
        )
        self.nodes[name] = node
        self.temperature_history[name] = [temperature]
        return node

    def connect(self, a: str, b: str):
        if a in self.nodes and b in self.nodes:
            if b not in self.nodes[a].connections:
                self.nodes[a].connections.append(b)
            if a not in self.nodes[b].connections:
                self.nodes[b].connections.append(a)

    def apply_heat(self, name: str, heat: float):
        if name in self.nodes:
            self.nodes[name].heat_generated += heat

    def step(self, dt: float = 0.1):
        self.time_step += 1
        new_temps: Dict[str, float] = {}

        for name, node in self.nodes.items():
            conduction = 0.0
            for neighbor_name in node.connections:
                if neighbor_name in self.nodes:
                    neighbor = self.nodes[neighbor_name]
                    temp_diff = neighbor.temperature - node.temperature
                    conduction += node.thermal_conductivity * temp_diff

            heating = node.heat_generated / max(node.heat_capacity, 0.001)
            cooling = -self.cooling_rate * (node.temperature - self.ambient_temp)
            delta_temp = (heating + conduction + cooling) * dt
            new_temps[name] = node.temperature + delta_temp

        for name, temp in new_temps.items():
            self.nodes[name].temperature = max(0.0, temp)
            self.nodes[name].heat_generated *= 0.9
            self.temperature_history[name].append(self.nodes[name].temperature)

    def thermal_flux(self, a: str, b: str) -> float:
        if a not in self.nodes or b not in self.nodes:
            return 0.0
        return (self.nodes[b].temperature - self.nodes[a].temperature) * \
               self.nodes[a].thermal_conductivity

    def hotspots(self, threshold: float = 50.0) -> List[ThermalReading]:
        results = []
        for name, node in self.nodes.items():
            flux = sum(self.thermal_flux(name, c) for c in node.connections)
            if node.temperature > threshold:
                results.append(ThermalReading(
                    name=name, temperature=node.temperature,
                    heat_generated=node.heat_generated,
                    neighbors=len(node.connections),
                    thermal_flux=flux,
                ))
        return sorted(results, key=lambda r: r.temperature, reverse=True)

    def cold_zones(self, threshold: float = 15.0) -> List[ThermalReading]:
        results = []
        for name, node in self.nodes.items():
            flux = sum(self.thermal_flux(name, c) for c in node.connections)
            if node.temperature < threshold:
                results.append(ThermalReading(
                    name=name, temperature=node.temperature,
                    heat_generated=node.heat_generated,
                    neighbors=len(node.connections),
                    thermal_flux=flux,
                ))
        return sorted(results, key=lambda r: r.temperature)

    def equilibrium_state(self) -> Dict[str, Any]:
        temps = [n.temperature for n in self.nodes.values()]
        return {
            "time_steps": self.time_step,
            "node_count": len(self.nodes),
            "avg_temp": sum(temps) / max(len(temps), 1),
            "max_temp": max(temps) if temps else 0,
            "min_temp": min(temps) if temps else 0,
            "temp_variance": (
                sum((t - sum(temps)/len(temps))**2 for t in temps) / len(temps)
                if temps else 0
            ),
        }

    def simulate(self, steps: int, dt: float = 0.1) -> Dict:
        for _ in range(steps):
            self.step(dt)
        return self.equilibrium_state()

    def export_temperature_map(self) -> List[Dict]:
        return [
            {"name": n.name, "temp": round(n.temperature, 2),
             "connections": len(n.connections)}
            for n in sorted(self.nodes.values(), key=lambda n: n.temperature, reverse=True)
        ]


from typing import Any


def demo():
    engine = ThermalDynamicsEngine(ambient_temp=20.0, cooling_rate=0.005)
    print("=== Thermal Dynamics Engine ===")
    modules = [
        ("photon_memory", 1.2, 0.15), ("dark_mapper", 0.8, 0.1),
        ("tardigrade", 1.5, 0.12), ("coral_reef", 0.9, 0.08),
        ("neutron_core", 2.0, 0.2), ("consciousness", 1.8, 0.18),
        ("hex_vm", 1.1, 0.14), ("pipeline", 1.3, 0.11),
        ("meme_engine", 0.7, 0.09), ("temporal_echo", 0.6, 0.07),
    ]
    for name, capacity, cond in modules:
        engine.add_node(name, temperature=20.0, heat_capacity=capacity, conductivity=cond)

    connections = [
        ("photon_memory", "neutron_core"), ("dark_mapper", "consciousness"),
        ("tardigrade", "coral_reef"), ("hex_vm", "pipeline"),
        ("meme_engine", "temporal_echo"), ("consciousness", "photon_memory"),
        ("pipeline", "neutron_core"),
    ]
    for a, b in connections:
        engine.connect(a, b)

    engine.apply_heat("neutron_core", 50.0)
    engine.apply_heat("consciousness", 40.0)
    engine.apply_heat("photon_memory", 30.0)

    result = engine.simulate(steps=20, dt=0.1)
    print(f"  Steps: {result['time_steps']}, Nodes: {result['node_count']}")
    print(f"  Avg temp: {result['avg_temp']:.2f}°C")
    print(f"  Max temp: {result['max_temp']:.2f}°C, Min: {result['min_temp']:.2f}°C")
    print(f"  Variance: {result['temp_variance']:.4f}")

    print("\nHotspots (>50°C):")
    for h in engine.hotspots(50.0):
        print(f"  {h.name}: {h.temperature:.2f}°C (flux={h.thermal_flux:.4f})")

    print("\nCold zones (<25°C):")
    for c in engine.cold_zones(25.0):
        print(f"  {c.name}: {c.temperature:.2f}°C")

    print("\nTemperature map:")
    for entry in engine.export_temperature_map()[:5]:
        print(f"  {entry['name']}: {entry['temp']}°C ({entry['connections']} connections)")

    return result


if __name__ == "__main__":
    demo()
