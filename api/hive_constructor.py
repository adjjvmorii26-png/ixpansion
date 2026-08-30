"""Hive Constructor — agents collectively build complex structures without a blueprint.

Agents contribute building blocks to a shared construction site. No single
agent knows the final shape — it emerges from local rules and neighbor
influence. The hive builds cathedrals of code from swarm intelligence.
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

BLOCK_TYPES = {
    "foundation": {"strength": 3.0, "weight": 2.0, "color": "#8B4513"},
    "pillar": {"strength": 2.5, "weight": 1.5, "color": "#A0522D"},
    "arch": {"strength": 1.5, "weight": 1.0, "color": "#CD853F"},
    "spire": {"strength": 1.0, "weight": 0.5, "color": "#DEB887"},
    "bridge": {"strength": 2.0, "weight": 1.2, "color": "#D2691E"},
    "ornament": {"strength": 0.5, "weight": 0.3, "color": "#FFD700"},
}


class BuildingBlock:
    def __init__(self, agent_id: str, block_type: str, position: Tuple[int, int, int]):
        self.agent_id = agent_id
        self.block_type = block_type
        self.position = position
        self.specs = BLOCK_TYPES.get(block_type, BLOCK_TYPES["foundation"])
        self.id = hashlib.sha256(f"{agent_id}:{position}".encode()).hexdigest()[:8]
        self.placed_at = time.time()
        self.neighbors: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "type": self.block_type,
            "position": self.position,
            "strength": self.specs["strength"],
            "color": self.specs["color"],
            "neighbors": len(self.neighbors),
        }


class HiveConstructor:
    def __init__(self):
        self.blocks: Dict[str, BuildingBlock] = {}
        self.position_map: Dict[Tuple[int, int, int], str] = {}
        self.contributors: Dict[str, int] = {}
        self.construction_log: List[Dict[str, Any]] = []

    def place_block(self, agent_id: str, block_type: str, position: Tuple[int, int, int]) -> Dict[str, Any]:
        if position in self.position_map:
            return {"error": "position occupied"}
        block = BuildingBlock(agent_id, block_type, position)
        self.blocks[block.id] = block
        self.position_map[position] = block.id
        self.contributors[agent_id] = self.contributors.get(agent_id, 0) + 1
        self._connect_neighbors(block)
        self.construction_log.append({
            "event": "block_placed",
            "agent": agent_id,
            "type": block_type,
            "position": position,
            "time": time.time(),
        })
        return {"placed": block.to_dict()}

    def _connect_neighbors(self, block: BuildingBlock):
        x, y, z = block.position
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                for dz in [-1, 0, 1]:
                    if dx == 0 and dy == 0 and dz == 0:
                        continue
                    neighbor_pos = (x + dx, y + dy, z + dz)
                    if neighbor_pos in self.position_map:
                        neighbor_id = self.position_map[neighbor_pos]
                        if neighbor_id in self.blocks:
                            block.neighbors.append(neighbor_id)
                            self.blocks[neighbor_id].neighbors.append(block.id)

    def structural_integrity(self) -> Dict[str, Any]:
        if not self.blocks:
            return {"integrity": 0, "message": "empty construction site"}
        total_strength = sum(b.specs["strength"] for b in self.blocks.values())
        avg_connections = sum(len(b.neighbors) for b in self.blocks.values()) / len(self.blocks)
        total_weight = sum(b.specs["weight"] for b in self.blocks.values())
        foundation_count = sum(1 for b in self.blocks.values() if b.block_type == "foundation")
        height = max((b.position[2] for b in self.blocks.values()), default=0) + 1
        integrity_score = min(1.0, (total_strength * avg_connections) / (total_weight * height + 1))
        return {
            "total_blocks": len(self.blocks),
            "total_strength": round(total_strength, 2),
            "total_weight": round(total_weight, 2),
            "avg_connections": round(avg_connections, 2),
            "height": height,
            "foundation_count": foundation_count,
            "integrity_score": round(integrity_score, 4),
        }

    def contributor_rankings(self) -> List[Dict[str, Any]]:
        return sorted(
            [{"agent": k, "blocks_placed": v} for k, v in self.contributors.items()],
            key=lambda x: x["blocks_placed"],
            reverse=True,
        )

    def blueprint_emergence(self) -> Dict[str, Any]:
        """Detect what pattern the hive is unconsciously building."""
        type_counts = {}
        for block in self.blocks.values():
            type_counts[block.block_type] = type_counts.get(block.block_type, 0) + 1
        dominant = max(type_counts, key=type_counts.get) if type_counts else "none"
        patterns = {
            "foundation": "cathedral",
            "pillar": "colonnade",
            "arch": "aqueduct",
            "spire": "observatory",
            "bridge": "network",
            "ornament": "garden",
        }
        return {
            "emerging_pattern": patterns.get(dominant, "unknown"),
            "type_distribution": type_counts,
            "dominant_block": dominant,
        }


_constructor = HiveConstructor()


def hive_constructor_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "place":
        return _constructor.place_block(
            payload.get("agent_id", "builder"),
            payload.get("block_type", "foundation"),
            tuple(payload.get("position", [0, 0, 0])),
        )
    elif action == "integrity":
        return _constructor.structural_integrity()
    elif action == "rankings":
        return {"rankings": _constructor.contributor_rankings()}
    elif action == "blueprint":
        return _constructor.blueprint_emergence()
    return {"status": "active", **_constructor.structural_integrity()}


handler = hive_constructor_handler


def coherence_vitals() -> dict:
    """hive_constructor reports its vital signs to the living system."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "hive_constructor_vitality": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "germination_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships, auto-picked from shared domain language."""
    return ['neural_pathway', 'neural_fabric', 'entropy_gardener']

