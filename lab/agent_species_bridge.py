"""Agent Species Bridge — Connects omega_prime's agent species to the lab system.

Bridges Sentinel, Architect, and Wanderer species into the sandbox engine,
enabling their deliberation and behavior systems to be tested.
"""
from __future__ import annotations
import hashlib
import random
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


class InferenceRule:
    def __init__(self, condition, conclusion):
        self.condition = condition
        self.conclusion = conclusion


class InferenceEngine:
    def __init__(self):
        self.rules: list[InferenceRule] = []

    def add_rule(self, condition, conclusion):
        self.rules.append(InferenceRule(condition, conclusion))

    def fire(self, facts: dict) -> set[str]:
        conclusions = set()
        for rule in self.rules:
            try:
                if rule.condition(facts):
                    conclusions.add(rule.conclusion)
            except Exception:
                pass
        return conclusions


class AgentSpecies:
    def __init__(self, agent_id: str, species: str, seed: int = 42):
        self.id = agent_id
        self.species = species
        self.seed = seed
        self.rng = random.Random(seed + hash(agent_id))
        self.stimulus: dict[str, Any] = {}
        self.memory: list[dict] = []
        self.energy = 1.0
        self.age = 0
        self.engine = InferenceEngine()
        self._setup_rules()

    def _setup_rules(self):
        if self.species == "sentinel":
            self.engine.add_rule(lambda f: f.get("threat_level", 0) > 5, "raise_alarm")
            self.engine.add_rule(lambda f: f.get("anomaly_count", 0) > 3, "investigate")
        elif self.species == "architect":
            self.engine.add_rule(lambda f: f.get("complexity", 0) > 0.7, "refactor")
            self.engine.add_rule(lambda f: f.get("duplications", 0) > 2, "consolidate")
        elif self.species == "wanderer":
            self.engine.add_rule(lambda f: f.get("novelty", 0) > 0.8, "explore")
            self.engine.add_rule(lambda f: f.get("familiarity", 0) > 0.9, "drift")

    def perceive(self, environment: dict):
        self.stimulus.update(environment)

    def deliberate(self) -> dict:
        conclusions = self.engine.fire(self.stimulus)
        intent = "observe"
        if "raise_alarm" in conclusions:
            intent = "alert"
        elif "refactor" in conclusions:
            intent = "restructure"
        elif "explore" in conclusions:
            intent = "venture"
        elif "investigate" in conclusions:
            intent = "probe"
        elif "consolidate" in conclusions:
            intent = "merge"
        elif "drift" in conclusions:
            intent = "wander"
        return {"intent": intent, "conclusions": list(conclusions), "species": self.species}

    def act(self) -> dict:
        self.age += 1
        self.energy -= 0.005
        decision = self.deliberate()
        action = {
            "agent_id": self.id,
            "species": self.species,
            "tick": self.age,
            "decision": decision,
            "energy": round(self.energy, 4),
        }
        self.memory.append(action)
        return action

    def to_dict(self) -> dict:
        return {
            "id": self.id, "species": self.species,
            "age": self.age, "energy": round(self.energy, 4),
            "memory_size": len(self.memory),
        }


class SpeciesBridge:
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.agents: dict[str, AgentSpecies] = {}
        self.species_counts: dict[str, int] = {}

    def spawn(self, species: str, count: int = 3) -> list[AgentSpecies]:
        spawned = []
        for i in range(count):
            idx = self.species_counts.get(species, 0)
            agent = AgentSpecies(f"{species}_{idx}", species, self.seed + idx)
            self.agents[agent.id] = agent
            self.species_counts[species] = idx + 1
            spawned.append(agent)
        return spawned

    def tick(self, environment: dict | None = None) -> dict:
        env = environment or {}
        actions = []
        for agent in self.agents.values():
            agent.perceive(env)
            action = agent.act()
            actions.append(action)
        return {
            "tick": actions[0]["tick"] if actions else 0,
            "agent_count": len(self.agents),
            "actions": actions,
        }

    def simulate(self, ticks: int = 10, environment: dict | None = None) -> dict:
        results = []
        for _ in range(ticks):
            result = self.tick(environment)
            results.append(result)
        return {
            "ticks": ticks,
            "final_agents": [a.to_dict() for a in self.agents.values()],
            "species_summary": {s: len([a for a in self.agents.values() if a.species == s])
                               for s in self.species_counts},
        }

    def report(self) -> dict:
        return {
            "bridge": "agent_species_bridge",
            "total_agents": len(self.agents),
            "species": {s: c for s, c in self.species_counts.items()},
            "agents": [a.to_dict() for a in list(self.agents.values())[:10]],
        }


def demo():
    bridge = SpeciesBridge(seed=42)
    bridge.spawn("sentinel", 3)
    bridge.spawn("architect", 2)
    bridge.spawn("wanderer", 4)

    # Simulate with varying environments
    envs = [
        {"threat_level": 7, "complexity": 0.8, "novelty": 0.9},
        {"threat_level": 2, "complexity": 0.9, "duplications": 4},
        {"threat_level": 1, "novelty": 0.3, "familiarity": 0.95},
    ]
    sim = bridge.simulate(ticks=10, environment=envs[0])
    return {"bridge_report": bridge.report(), "simulation": {k: v for k, v in sim.items() if k != "final_agents"}}


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
