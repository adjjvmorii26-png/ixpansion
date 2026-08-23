from __future__ import annotations
from typing import Any

from agents.architect import Architect
from agents.base import Agent
from agents.glitcher import Glitcher
from agents.mutator import Mutator
from agents.observer import Observer
from core.events import EventBus
from core.state_graph import StateGraph
from expansion.models.mutation import Mutation
from expansion.rule_engine import RuleEngine
from glitch.divergence_tracker import DivergenceTracker
from hex.vm import HexVM
from mesh.channels import MeshChannels
from mesh.topology import build_topology
from worlds.world_state import WorldState


class IxpansionRuntime:
    """A deterministic loop connecting agents, worlds, mesh, HEX and mutation."""

    def __init__(self, scene: str = "hex_storm", topology: str = "star", seed: int = 42) -> None:
        self.seed = seed
        self.graph = StateGraph()
        self.graph.add_node("origin", "core", stability=1.0, energy=10)
        self.bus = EventBus()
        self.mesh = MeshChannels(build_topology(topology, ["origin", "alpha", "beta"]))
        self.world = WorldState(scene)
        self.agents: list[Agent] = [Observer(), Architect(), Mutator(), Glitcher()]
        self.rules = RuleEngine()
        self.tracker = DivergenceTracker()
        self.vm = HexVM()
        self.ticks = 0

    def _apply_action(self, action: dict[str, Any]) -> dict[str, Any] | None:
        kind = action.get("type")
        if kind == "spawn":
            node_id = str(action["node"])
            if node_id not in self.graph.nodes:
                self.graph.add_node(node_id, str(action.get("kind", "region")), stability=0.8)
                self.graph.connect("origin", node_id, "growth")
            return {"delivered": True}
        if kind == "mutate":
            mutation = Mutation(
                target=str(action["node"]), operation=str(action.get("operation", "add")),
                field=str(action.get("field", "energy")), value=action.get("value", 1),
            )
            node = self.graph.nodes.get(mutation.target)
            if node:
                current = node.state.get(mutation.field, 0)
                node.state[mutation.field] = current + int(mutation.value)
            return {"applied": node is not None}
        if kind == "anomaly":
            target = self.graph.nodes.get(str(action.get("node", "origin")))
            if target:
                target.state["anomaly"] = action.get("value", "identity-split")
            return {"injected": target is not None}
        return None

    def tick(self) -> dict[str, Any]:
        self.ticks += 1
        perception = self.world.tick(self.ticks, self.graph)
        results: list[Any] = []
        for agent in self.agents:
            for action in agent.act(perception):
                delivered = self.mesh.broadcast(agent.name, action)
                outcome = self._apply_action(action)
                results.append({"agent": agent.name, "action": action, "delivered": delivered, "outcome": outcome})
                self.bus.publish(f"agent.{agent.name}", {"tick": self.ticks, "action": action})
        triggered = self.rules.evaluate(self.graph)
        anomalies = self.tracker.observe(self.ticks, self.graph.fingerprint())
        return {
            "tick": self.ticks,
            "scene": self.world.scene,
            "perception": perception,
            "results": results,
            "triggered_rules": triggered,
            "anomalies": anomalies,
            "fingerprint": self.graph.fingerprint(),
            "vm_outputs": self.vm.outputs,
        }

    def run(self, ticks: int = 3) -> list[dict[str, Any]]:
        if ticks < 1:
            raise ValueError("ticks must be positive")
        return [self.tick() for _ in range(ticks)]
