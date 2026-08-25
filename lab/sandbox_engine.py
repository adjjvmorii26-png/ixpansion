"""Sandbox Execution Engine — Spawns agents into realms and runs simulations.

Connects omega_prime's realm system with the agent ecosystem, enabling
live simulation runs with configurable parameters.
"""
from __future__ import annotations
import hashlib
import random
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


class Agent:
    """A lightweight agent for sandbox execution."""

    def __init__(self, agent_id: str, agent_type: str, genome: dict[str, float] | None = None, seed: int = 42):
        self.id = agent_id
        self.agent_type = agent_type
        self.genome = genome or {"energy": 1.0, "cognition": 0.5, "social": 0.3, "adaptation": 0.4}
        self.state = "dormant"
        self.energy = self.genome.get("energy", 1.0)
        self.memory: list[dict] = []
        self.position = (0, 0)
        self.age = 0
        self.rng = random.Random(seed + hash(agent_id))

    def act(self, environment: dict) -> dict:
        """Execute one tick of agent behavior."""
        self.age += 1
        self.energy -= 0.01

        action = {
            "agent_id": self.id,
            "tick": self.age,
            "position": self.position,
            "energy": round(self.energy, 4),
        }

        # Behavior based on agent type
        if self.agent_type == "scout":
            # Scout moves randomly and discovers
            dx = self.rng.choice([-1, 0, 1])
            dy = self.rng.choice([-1, 0, 1])
            self.position = (self.position[0] + dx, self.position[1] + dy)
            action["movement"] = (dx, dy)
            action["discovered"] = self.rng.random() > 0.7

        elif self.agent_type == "analyst":
            # Analyst stays put and processes
            action["analyzed"] = True
            action["insight"] = self.rng.random()

        elif self.agent_type == "builder":
            # Builder constructs
            action["built"] = True
            action["construction"] = self.rng.choice(["wall", "bridge", "tower", "garden"])

        elif self.agent_type == "sentinel":
            # Sentinel watches and protects
            action["watching"] = True
            action["threats_detected"] = self.rng.randint(0, 2)

        else:
            # Default: wander
            dx = self.rng.choice([-1, 0, 1])
            dy = self.rng.choice([-1, 0, 1])
            self.position = (self.position[0] + dx, self.position[1] + dy)

        self.state = "active" if self.energy > 0 else "depleted"
        self.memory.append(action)
        return action

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.agent_type,
            "state": self.state,
            "energy": round(self.energy, 4),
            "age": self.age,
            "position": self.position,
        }


class Realm:
    """A simulated environment for agent execution."""

    def __init__(self, name: str, width: int = 10, height: int = 10, seed: int = 42):
        self.name = name
        self.width = width
        self.height = height
        self.grid = [[0.0] * width for _ in range(height)]
        self.agents: dict[str, Agent] = {}
        self.events: list[dict] = []
        self.epoch = 0
        self.rng = random.Random(seed)

        # Initialize grid with random terrain
        for y in range(height):
            for x in range(width):
                self.grid[y][x] = self.rng.random()

    def spawn_agent(self, agent: Agent):
        """Place an agent in the realm."""
        x = self.rng.randint(0, self.width - 1)
        y = self.rng.randint(0, self.height - 1)
        agent.position = (x, y)
        self.agents[agent.id] = agent

    def tick(self) -> dict:
        """Advance the realm by one tick."""
        self.epoch += 1
        actions = []

        for agent_id, agent in list(self.agents.items()):
            if agent.state == "depleted":
                continue
            environment = {"grid": self.grid, "epoch": self.epoch}
            action = agent.act(environment)
            actions.append(action)

            # Grid interaction
            x, y = agent.position
            if 0 <= x < self.width and 0 <= y < self.height:
                self.grid[y][x] = max(0, min(1, self.grid[y][x] + 0.01))

        # Check for agent interactions
        positions = {}
        for agent in self.agents.values():
            if agent.state != "depleted":
                pos = agent.position
                if pos not in positions:
                    positions[pos] = []
                positions[pos].append(agent.id)

        interactions = []
        for pos, agent_ids in positions.items():
            if len(agent_ids) > 1:
                interactions.append({"position": pos, "agents": agent_ids, "type": "encounter"})

        event = {
            "epoch": self.epoch,
            "agent_count": len([a for a in self.agents.values() if a.state != "depleted"]),
            "actions": len(actions),
            "interactions": len(interactions),
            "interactions_detail": interactions,
        }
        self.events.append(event)
        return event

    def observation(self) -> dict:
        """Get current realm state."""
        active = [a.to_dict() for a in self.agents.values() if a.state != "depleted"]
        depleted = [a.to_dict() for a in self.agents.values() if a.state == "depleted"]
        return {
            "realm": self.name,
            "epoch": self.epoch,
            "dimensions": (self.width, self.height),
            "active_agents": active,
            "depleted_agents": depleted,
            "total_events": len(self.events),
        }


class SandboxEngine:
    """Top-level engine that manages realms and simulation runs."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.realms: dict[str, Realm] = {}
        self.run_history: list[dict] = []

    def create_realm(self, name: str, width: int = 10, height: int = 10) -> Realm:
        realm = Realm(name, width, height, self.seed)
        self.realms[name] = realm
        return realm

    def populate_realm(self, realm_name: str, agents_per_type: dict[str, int] | None = None):
        """Spawn agents into a realm."""
        if realm_name not in self.realms:
            return
        realm = self.realms[realm_name]
        agents_per_type = agents_per_type or {"scout": 2, "analyst": 1, "builder": 1, "sentinel": 1}

        agent_count = 0
        for agent_type, count in agents_per_type.items():
            for i in range(count):
                agent = Agent(
                    f"{agent_type}_{i}", agent_type,
                    seed=self.seed + agent_count,
                )
                realm.spawn_agent(agent)
                agent_count += 1

    def run_simulation(self, realm_name: str, ticks: int = 10) -> dict:
        """Run a full simulation in a realm."""
        if realm_name not in self.realms:
            return {"error": f"realm '{realm_name}' not found"}

        realm = self.realms[realm_name]
        t0 = time.time()
        tick_results = []

        for _ in range(ticks):
            event = realm.tick()
            tick_results.append(event)

        elapsed = time.time() - t0
        final_state = realm.observation()

        run = {
            "realm": realm_name,
            "ticks": ticks,
            "elapsed_ms": round(elapsed * 1000, 2),
            "final_epoch": realm.epoch,
            "final_agent_count": final_state["active_agents"],
            "total_interactions": sum(t["interactions"] for t in tick_results),
            "tick_results": tick_results,
        }
        self.run_history.append(run)
        return run

    def report(self) -> dict:
        """Generate engine report."""
        return {
            "engine": "sandbox_engine",
            "realm_count": len(self.realms),
            "realms": {name: r.observation() for name, r in self.realms.items()},
            "run_count": len(self.run_history),
            "total_ticks": sum(r["ticks"] for r in self.run_history),
        }


def demo():
    engine = SandboxEngine(seed=42)

    # Create and populate realms
    void = engine.create_realm("void", 8, 8)
    lattice = engine.create_realm("lattice", 6, 6)

    engine.populate_realm("void", {"scout": 3, "analyst": 2, "builder": 1})
    engine.populate_realm("lattice", {"sentinel": 2, "scout": 2})

    # Run simulations
    void_run = engine.run_simulation("void", ticks=10)
    lattice_run = engine.run_simulation("lattice", ticks=8)

    return {
        "engine_report": engine.report(),
        "void_run": {k: v for k, v in void_run.items() if k != "tick_results"},
        "lattice_run": {k: v for k, v in lattice_run.items() if k != "tick_results"},
    }


def main():
    import json
    result = demo()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
