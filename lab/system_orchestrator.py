"""System Orchestrator — Unified bridge manager that connects all subsystems.

Coordinates the sandbox engine, reactor bridge, kernel bridge, messaging,
cognition, and agent species into a single coherent system.
"""
from __future__ import annotations
import hashlib
import random
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


class SystemOrchestrator:
    def __init__(self, seed=42):
        self.seed = seed
        self.state = {
            "epoch": 0, "mode": "dormant",
            "entropy": 0.0, "cohesion": 1.0,
            "active_subsystems": [],
        }
        self.events: list[dict] = []
        self.subsystems: dict[str, dict] = {}
        self.tick_count = 0

    def register_subsystem(self, name: str, status: str = "ready"):
        self.subsystems[name] = {"status": status, "last_tick": 0, "events": 0}

    def emit_event(self, source: str, event_type: str, payload: dict):
        event = {
            "epoch": self.tick_count, "source": source,
            "type": event_type, "payload": payload,
            "timestamp": time.time(),
        }
        self.events.append(event)
        if source in self.subsystems:
            self.subsystems[source]["events"] += 1

    def tick(self) -> dict:
        self.tick_count += 1
        self.state["epoch"] = self.tick_count
        self.state["entropy"] += random.Random(self.tick_count).uniform(-0.01, 0.015)
        self.state["entropy"] = max(0, min(1, self.state["entropy"]))
        self.state["cohesion"] = max(0, min(1, 1.0 - self.state["entropy"] * 0.5))
        active = [n for n, s in self.subsystems.items() if s["status"] == "active"]
        self.state["active_subsystems"] = active
        for name in self.subsystems:
            if self.subsystems[name]["status"] == "ready" and random.Random(self.tick_count + hash(name)).random() > 0.8:
                self.subsystems[name]["status"] = "active"
                self.emit_event(name, "activated", {})
        for name, sub in self.subsystems.items():
            sub["last_tick"] = self.tick_count
        return {
            "tick": self.tick_count,
            "entropy": round(self.state["entropy"], 4),
            "cohesion": round(self.state["cohesion"], 4),
            "active": len(active),
        }

    def simulate(self, ticks=10) -> dict:
        results = []
        for _ in range(ticks):
            results.append(self.tick())
        return {
            "ticks": ticks,
            "final_state": dict(self.state),
            "total_events": len(self.events),
            "subsystem_summary": {n: {"status": s["status"], "events": s["events"]}
                                  for n, s in self.subsystems.items()},
        }

    def report(self) -> dict:
        return {
            "orchestrator": "system_orchestrator",
            "ticks": self.tick_count,
            "subsystems": len(self.subsystems),
            "events": len(self.events),
            "state": {k: round(v, 4) if isinstance(v, float) else v for k, v in self.state.items()},
        }


def demo():
    orch = SystemOrchestrator(seed=42)
    for name in ["sandbox", "reactors", "kernel", "messaging", "cognition", "agents", "pipeline", "constellation"]:
        orch.register_subsystem(name)
    orch.emit_event("sandbox", "initialized", {"realms": 2})
    orch.emit_event("kernel", "state_loaded", {"epoch": 0})
    sim = orch.simulate(ticks=20)
    return {"simulation": sim, "report": orch.report()}


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
