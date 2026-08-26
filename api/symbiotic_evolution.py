"""Symbiotic Evolution — agents co-evolve by forming dependency bonds.

Agents form symbiotic relationships: mutualism (both benefit),
parasitism (one benefits at the other's expense), or commensalism
(one benefits, other unaffected). Over time, symbiotic bonds reshape
agent capabilities and create emergent super-organisms.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SYMBIOSIS_TYPES = {
    "mutualism": {"benefit_a": 1.0, "benefit_b": 1.0, "cost_a": 0.3, "cost_b": 0.3},
    "parasitism": {"benefit_a": 1.5, "benefit_b": -0.5, "cost_a": 0.1, "cost_b": 0.8},
    "commensalism": {"benefit_a": 1.0, "benefit_b": 0.0, "cost_a": 0.2, "cost_b": 0.0},
    "competition": {"benefit_a": 0.5, "benefit_b": 0.5, "cost_a": 0.7, "cost_b": 0.7},
}


class SymbioticBond:
    def __init__(self, agent_a: str, agent_b: str, bond_type: str = "mutualism"):
        self.agent_a = agent_a
        self.agent_b = agent_b
        self.bond_type = bond_type
        self.strength = 1.0
        self.age = 0
        self.timestamp = time.time()
        self.id = hashlib.sha256(f"{agent_a}:{agent_b}:{self.timestamp}".encode()).hexdigest()[:10]
        specs = SYMBIOSIS_TYPES.get(bond_type, SYMBIOSIS_TYPES["mutualism"])
        self.params = specs.copy()

    def evolve(self) -> Dict[str, Any]:
        """Bond evolves — strength changes based on type."""
        self.age += 1
        if self.bond_type == "mutualism":
            self.strength *= random.uniform(1.0, 1.1)
        elif self.bond_type == "parasitism":
            self.strength *= random.uniform(0.95, 1.05)
        elif self.bond_type == "competition":
            self.strength *= random.uniform(0.9, 1.1)
        self.strength = min(max(self.strength, 0.0), 5.0)
        return {
            "bond_id": self.id,
            "strength": round(self.strength, 3),
            "age": self.age,
            "type": self.bond_type,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_a": self.agent_a,
            "agent_b": self.agent_b,
            "type": self.bond_type,
            "strength": round(self.strength, 3),
            "age": self.age,
            "params": self.params,
        }


class SymbioticEvolver:
    def __init__(self):
        self.bonds: Dict[str, SymbioticBond] = {}
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.super_organisms: List[Dict[str, Any]] = []

    def register_agent(self, agent_id: str, capabilities: List[str] = None) -> Dict[str, Any]:
        self.agents[agent_id] = {
            "capabilities": capabilities or [],
            "fitness": 1.0,
            "bonds": [],
            "birth_time": time.time(),
        }
        return {"agent_id": agent_id, "capabilities": capabilities or []}

    def form_bond(self, agent_a: str, agent_b: str, bond_type: str = "mutualism") -> Dict[str, Any]:
        if agent_a not in self.agents or agent_b not in self.agents:
            return {"error": "agent not found"}
        bond = SymbioticBond(agent_a, agent_b, bond_type)
        self.bonds[bond.id] = bond
        self.agents[agent_a]["bonds"].append(bond.id)
        self.agents[agent_b]["bonds"].append(bond.id)
        if bond_type == "mutualism":
            self.agents[agent_a]["fitness"] *= 1.05
            self.agents[agent_b]["fitness"] *= 1.05
        elif bond_type == "parasitism":
            self.agents[agent_a]["fitness"] *= 1.1
            self.agents[agent_b]["fitness"] *= 0.9
        return {"bond": bond.to_dict()}

    def evolve_bonds(self) -> List[Dict[str, Any]]:
        results = []
        for bond in self.bonds.values():
            results.append(bond.evolve())
            # Update agent fitness based on evolved bond
            if bond.agent_a in self.agents:
                self.agents[bond.agent_a]["fitness"] *= (1 + (bond.strength - 1) * 0.01)
            if bond.agent_b in self.agents:
                self.agents[bond.agent_b]["fitness"] *= (1 + (bond.strength - 1) * 0.01)
        # Check for super-organisms (fully connected mutualism clusters)
        self._detect_super_organisms()
        return results

    def _detect_super_organisms(self):
        mutualism_graph: Dict[str, set] = {}
        for bond in self.bonds.values():
            if bond.bond_type == "mutualism" and bond.strength > 2.0:
                mutualism_graph.setdefault(bond.agent_a, set()).add(bond.agent_b)
                mutualism_graph.setdefault(bond.agent_b, set()).add(bond.agent_a)
        visited: set = set()
        for agent in mutualism_graph:
            if agent in visited:
                continue
            cluster = set()
            stack = [agent]
            while stack:
                current = stack.pop()
                if current in visited:
                    continue
                visited.add(current)
                cluster.add(current)
                for neighbor in mutualism_graph.get(current, set()):
                    if neighbor not in visited:
                        stack.append(neighbor)
            if len(cluster) >= 3:
                self.super_organisms.append({
                    "members": list(cluster),
                    "size": len(cluster),
                    "detected_at": time.time(),
                })

    def agent_report(self, agent_id: str) -> Optional[Dict[str, Any]]:
        if agent_id not in self.agents:
            return None
        info = self.agents[agent_id]
        agent_bonds = [self.bonds[bid].to_dict() for bid in info["bonds"] if bid in self.bonds]
        return {
            "agent_id": agent_id,
            "fitness": round(info["fitness"], 4),
            "capabilities": info["capabilities"],
            "active_bonds": len(agent_bonds),
            "bonds": agent_bonds,
        }

    def evolution_stats(self) -> Dict[str, Any]:
        bond_types = {}
        for bond in self.bonds.values():
            bond_types[bond.bond_type] = bond_types.get(bond.bond_type, 0) + 1
        return {
            "total_agents": len(self.agents),
            "total_bonds": len(self.bonds),
            "bond_types": bond_types,
            "super_organisms": len(self.super_organisms),
            "avg_fitness": round(
                sum(a["fitness"] for a in self.agents.values()) / max(len(self.agents), 1), 3
            ),
        }


_evolver = SymbioticEvolver()


def symbiotic_evolution_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "register":
        return _evolver.register_agent(
            payload.get("agent_id", f"agent_{random.randint(1000,9999)}"),
            payload.get("capabilities", []),
        )
    elif action == "bond":
        return _evolver.form_bond(
            payload.get("agent_a", ""), payload.get("agent_b", ""),
            payload.get("type", "mutualism"),
        )
    elif action == "evolve":
        return {"evolved": _evolver.evolve_bonds()}
    elif action == "report":
        return _evolver.agent_report(payload.get("agent_id", "")) or {"error": "agent not found"}
    return {"status": "active", **_evolver.evolution_stats()}
