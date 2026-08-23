from __future__ import annotations
from typing import Any

from core.state_graph import StateGraph


class WorldState:
    scenes = {
        "hex_storm": {"focus": "origin", "entropy": 0.42},
        "mesh_fracture": {"focus": "alpha", "fracture": 0.3},
        "overgrowth_field": {"focus": "beta", "growth": 1.2},
    }

    def __init__(self, scene: str = "hex_storm") -> None:
        if scene not in self.scenes:
            raise KeyError(f"unknown scene: {scene}")
        self.scene = scene
        self.base = dict(self.scenes[scene])

    def tick(self, tick: int, graph: StateGraph) -> dict[str, Any]:
        perception = {"tick": tick, "scene": self.scene, **self.base, "fingerprint": graph.fingerprint()}
        if self.scene == "hex_storm":
            perception["entropy"] = min(1.0, float(self.base["entropy"]) + tick / 100)
        elif self.scene == "mesh_fracture":
            perception["fracture"] = min(1.0, float(self.base["fracture"]) + tick / 80)
        else:
            perception["growth"] = float(self.base["growth"]) + tick / 20
        return perception
