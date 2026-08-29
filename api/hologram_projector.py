"""Hologram Projector — creates interactive 3D representations of system state.

Agents can project holograms of any subsystem — rotating, zooming,
inspecting internal states. Holograms are shared across all observers,
creating a common operational picture that enhances collective decision-making.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class Hologram:
    def __init__(self, name: str, source_data: Dict[str, Any], projector: str):
        self.name = name
        self.source_data = source_data
        self.projector = projector
        self.observers: List[str] = []
        self.rotations: List[Dict[str, float]] = []
        self.annotations: List[Dict[str, str]] = []
        self.created_at = time.time()
        self.id = hashlib.sha256(f"{name}:{self.created_at}".encode()).hexdigest()[:8]
        self.resolution = random.choice(["low", "medium", "high", "ultra"])

    def observe(self, agent_id: str) -> Dict[str, Any]:
        if agent_id not in self.observers:
            self.observers.append(agent_id)
        return {
            "hologram": self.name,
            "observer": agent_id,
            "resolution": self.resolution,
            "total_observers": len(self.observers),
        }

    def rotate(self, x: float, y: float, z: float) -> Dict[str, Any]:
        rotation = {"x": round(x, 2), "y": round(y, 2), "z": round(z, 2)}
        self.rotations.append(rotation)
        return {"rotated_to": rotation}

    def annotate(self, agent_id: str, text: str, position: Tuple[int, int, int] = None) -> Dict[str, Any]:
        annotation = {
            "agent": agent_id,
            "text": text,
            "position": list(position or (0, 0, 0)),
            "timestamp": time.time(),
        }
        self.annotations.append(annotation)
        return {"annotated": annotation}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "projector": self.projector,
            "observers": len(self.observers),
            "annotations": len(self.annotations),
            "resolution": self.resolution,
            "data_keys": list(self.source_data.keys()),
        }


class HologramProjector:
    def __init__(self):
        self.holograms: Dict[str, Hologram] = {}
        self.projection_log: List[Dict[str, Any]] = []

    def project(self, name: str, source_data: Dict[str, Any], projector: str) -> Dict[str, Any]:
        hologram = Hologram(name, source_data, projector)
        self.holograms[hologram.id] = hologram
        self.projection_log.append({
            "projected": name, "by": projector, "time": time.time(),
        })
        return {"hologram": hologram.to_dict()}

    def observe(self, hologram_id: str, agent_id: str) -> Dict[str, Any]:
        if hologram_id not in self.holograms:
            return {"error": "hologram not found"}
        return self.holograms[hologram_id].observe(agent_id)

    def rotate(self, hologram_id: str, x: float, y: float, z: float) -> Dict[str, Any]:
        if hologram_id not in self.holograms:
            return {"error": "hologram not found"}
        return self.holograms[hologram_id].rotate(x, y, z)

    def annotate(self, hologram_id: str, agent_id: str, text: str) -> Dict[str, Any]:
        if hologram_id not in self.holograms:
            return {"error": "hologram not found"}
        return self.holograms[hologram_id].annotate(agent_id, text)

    def gallery(self) -> List[Dict[str, Any]]:
        return [h.to_dict() for h in self.holograms.values()]

    def projector_stats(self) -> Dict[str, Any]:
        total_observers = sum(len(h.observers) for h in self.holograms.values())
        return {
            "total_holograms": len(self.holograms),
            "total_observations": total_observers,
            "total_annotations": sum(len(h.annotations) for h in self.holograms.values()),
            "total_projections": len(self.projection_log),
        }


_projector = HologramProjector()


def hologram_projector_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "project":
        return _projector.project(
            payload.get("name", "system_state"),
            payload.get("data", {}),
            payload.get("projector", "system"),
        )
    elif action == "observe":
        return _projector.observe(payload.get("hologram_id", ""), payload.get("agent_id", "viewer"))
    elif action == "rotate":
        return _projector.rotate(
            payload.get("hologram_id", ""),
            payload.get("x", 0), payload.get("y", 0), payload.get("z", 0),
        )
    elif action == "annotate":
        return _projector.annotate(
            payload.get("hologram_id", ""),
            payload.get("agent_id", "annotator"),
            payload.get("text", ""),
        )
    elif action == "gallery":
        return {"holograms": _projector.gallery()}
    return {"status": "active", **_projector.projector_stats()}


handler = hologram_projector_handler
