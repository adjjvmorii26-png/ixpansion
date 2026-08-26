"""Evolutionary Pressure — environmental forces that push agents to adapt or perish.

The system applies selectable pressures: resource scarcity, competition,
mutation rate, and environmental volatility. Agents that adapt survive;
those that don't get retired. The pressure engine ensures the ecosystem
never stagnates.
"""
from __future__ import annotations

import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class AgentPopulation:
    def __init__(self, agent_id: str, fitness: float = 1.0, traits: List[str] = None):
        self.agent_id = agent_id
        self.fitness = fitness
        self.traits = traits or []
        self.generation = 0
        self.stress_level = 0.0
        self.adaptations: List[str] = []
        self.alive = True
        self.birth_time = time.time()

    def apply_pressure(self, pressure_type: float) -> Dict[str, Any]:
        """Apply environmental pressure to this agent."""
        adaptation = random.random()
        if adaptation > pressure_type:
            self.fitness *= 1.1
            self.adaptations.append(f"resisted_{pressure_type:.2f}")
            result = "adapted"
        else:
            self.fitness *= 0.8
            self.stress_level += pressure_type * 0.3
            result = "stressed"
        if self.stress_level > 2.0:
            self.alive = False
            result = "retired"
        return {
            "agent_id": self.agent_id,
            "fitness": round(self.fitness, 4),
            "stress": round(self.stress_level, 4),
            "result": result,
        }

    def reproduce(self) -> "AgentPopulation":
        """Create offspring with mutated traits."""
        child_fitness = self.fitness * random.uniform(0.8, 1.2)
        child_traits = self.traits.copy()
        if child_traits and random.random() > 0.5:
            idx = random.randint(0, len(child_traits) - 1)
            child_traits[idx] = child_traits[idx] + "_mutant"
        return AgentPopulation(
            f"{self.agent_id}_gen{self.generation + 1}",
            child_fitness,
            child_traits,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "fitness": round(self.fitness, 4),
            "generation": self.generation,
            "stress": round(self.stress_level, 4),
            "alive": self.alive,
            "traits": self.traits,
            "adaptations": len(self.adaptations),
        }


class EvolutionaryPressureSystem:
    def __init__(self):
        self.population: Dict[str, AgentPopulation] = {}
        self.pressure_history: List[Dict[str, Any]] = []
        self.extinction_events: List[Dict[str, Any]] = []
        self.generation_count = 0

    def introduce(self, agent_id: str, fitness: float = 1.0, traits: List[str] = None) -> Dict[str, Any]:
        agent = AgentPopulation(agent_id, fitness, traits)
        self.population[agent_id] = agent
        return {"introduced": agent.to_dict()}

    def apply_global_pressure(self, pressure_type: str, intensity: float = 0.5) -> Dict[str, Any]:
        results = []
        for agent in list(self.population.values()):
            if agent.alive:
                result = agent.apply_pressure(intensity)
                results.append(result)
        alive_count = sum(1 for a in self.population.values() if a.alive)
        dead_count = len(self.population) - alive_count
        if dead_count > 0 and dead_count == len(self.population):
            self.extinction_events.append({
                "generation": self.generation_count,
                "pressure": pressure_type,
                "intensity": intensity,
                "time": time.time(),
            })
        self.pressure_history.append({
            "type": pressure_type,
            "intensity": intensity,
            "alive_after": alive_count,
            "dead_after": dead_count,
            "time": time.time(),
        })
        return {
            "pressure_applied": pressure_type,
            "intensity": intensity,
            "results": results,
            "alive": alive_count,
            "dead": dead_count,
        }

    def select_and_reproduce(self, top_n: int = 3) -> List[Dict[str, Any]]:
        """Survival of the fittest — top agents reproduce."""
        alive = [a for a in self.population.values() if a.alive]
        alive.sort(key=lambda a: a.fitness, reverse=True)
        survivors = alive[:top_n]
        offspring = []
        for agent in survivors:
            child = agent.reproduce()
            child.generation = agent.generation + 1
            self.population[child.agent_id] = child
            offspring.append(child.to_dict())
        self.generation_count += 1
        return offspring

    def ecosystem_stats(self) -> Dict[str, Any]:
        alive = [a for a in self.population.values() if a.alive]
        return {
            "total_agents": len(self.population),
            "alive": len(alive),
            "dead": len(self.population) - len(alive),
            "avg_fitness": round(
                sum(a.fitness for a in alive) / max(len(alive), 1), 4
            ),
            "generations": self.generation_count,
            "extinction_events": len(self.extinction_events),
            "pressure_events": len(self.pressure_history),
        }


_pressure_system = EvolutionaryPressureSystem()


def evolutionary_pressure_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "introduce":
        return _pressure_system.introduce(
            payload.get("agent_id", f"organism_{random.randint(1000,9999)}"),
            payload.get("fitness", 1.0),
            payload.get("traits", []),
        )
    elif action == "pressure":
        return _pressure_system.apply_global_pressure(
            payload.get("type", "scarcity"),
            payload.get("intensity", 0.5),
        )
    elif action == "reproduce":
        return {"offspring": _pressure_system.select_and_reproduce(payload.get("top_n", 3))}
    return {"status": "active", **_pressure_system.ecosystem_stats()}
