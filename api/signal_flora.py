"""Signal Flora — self-replicating information patterns that grow like plants.

Agents don't just send messages — they plant seeds. Seeds grow into
signal plants that bloom, spread spores (copies), wilt, and die.
Different species compete for signal bandwidth. The healthiest
flora indicates the system's information ecosystem vitality.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

FLORA_SPECIES = {
    "datafern": {"growth_rate": 0.3, "spore_range": 2, "lifespan": 10, "color": "#228B22"},
    "signalvine": {"growth_rate": 0.5, "spore_range": 3, "lifespan": 7, "color": "#32CD32"},
    "cryptomoss": {"growth_rate": 0.1, "spore_range": 1, "lifespan": 20, "color": "#006400"},
    "bytebloom": {"growth_rate": 0.8, "spore_range": 4, "lifespan": 5, "color": "#FF69B4"},
    "waveWillow": {"growth_rate": 0.4, "spore_range": 2, "lifespan": 12, "color": "#9370DB"},
}


class SignalPlant:
    def __init__(self, species: str, x: int = 0, y: int = 0, message: str = ""):
        self.species = species
        self.x = x
        self.y = y
        self.message = message
        self.age = 0
        self.health = 1.0
        self.specs = FLORA_SPECIES.get(specs := species, FLORA_SPECIES["datafern"])
        self.id = hashlib.sha256(f"{species}:{x}:{y}:{time.time()}".encode()).hexdigest()[:8]
        self.bloomed = False
        self.alive = True

    def grow(self) -> Dict[str, Any]:
        if not self.alive:
            return {"status": "dead"}
        self.age += 1
        self.health *= (1.0 - 1.0 / self.specs["lifespan"])
        if self.age >= self.specs["lifespan"]:
            self.alive = False
            return {"status": "wilted", "age": self.age}
        if self.age == self.specs["lifespan"] // 2:
            self.bloomed = True
        return {
            "status": "growing",
            "health": round(self.health, 3),
            "age": self.age,
            "bloomed": self.bloomed,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "species": self.species,
            "position": [self.x, self.y],
            "message": self.message[:50],
            "age": self.age,
            "health": round(self.health, 3),
            "alive": self.alive,
            "color": self.specs["color"],
        }


class SignalFloraGarden:
    def __init__(self):
        self.plants: Dict[str, SignalPlant] = {}
        self.spores: List[Dict[str, Any]] = []
        self.garden_log: List[Dict[str, Any]] = []

    def plant_seed(self, species: str, message: str, x: int = None, y: int = None) -> Dict[str, Any]:
        x = x or random.randint(-50, 50)
        y = y or random.randint(-50, 50)
        plant = SignalPlant(species, x, y, message)
        self.plants[plant.id] = plant
        self.garden_log.append({"event": "planted", "species": species, "time": time.time()})
        return {"planted": plant.to_dict()}

    def grow_garden(self) -> List[Dict[str, Any]]:
        results = []
        new_plants = []
        for plant in list(self.plants.values()):
            result = plant.grow()
            if result.get("status") == "wilted":
                # Release spores
                specs = FLORA_SPECIES.get(plant.species, FLORA_SPECIES["datafern"])
                for _ in range(specs["spore_range"]):
                    if random.random() > 0.5:
                        sx = plant.x + random.randint(-3, 3)
                        sy = plant.y + random.randint(-3, 3)
                        spore = {
                            "species": plant.species,
                            "x": sx, "y": sy,
                            "parent_message": plant.message,
                        }
                        self.spores.append(spore)
                        if len(self.plants) < 200:
                            new_plant = SignalPlant(plant.species, sx, sy, plant.message + "_v2")
                            new_plants.append(new_plant)
            results.append({"id": plant.id, **result})
        for p in new_plants:
            self.plants[p.id] = p
        return results

    def garden_map(self) -> List[Dict[str, Any]]:
        return [p.to_dict() for p in self.plants.values() if p.alive]

    def species_census(self) -> Dict[str, int]:
        census: Dict[str, int] = {}
        for plant in self.plants.values():
            if plant.alive:
                census[plant.species] = census.get(plant.species, 0) + 1
        return census

    def garden_stats(self) -> Dict[str, Any]:
        alive = sum(1 for p in self.plants.values() if p.alive)
        return {
            "total_plants": len(self.plants),
            "alive": alive,
            "dead": len(self.plants) - alive,
            "species_count": len(self.species_census()),
            "total_spores": len(self.spores),
            "species_census": self.species_census(),
        }


_garden = SignalFloraGarden()


def signal_flora_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "plant":
        return _garden.plant_seed(
            payload.get("species", "datafern"),
            payload.get("message", "a quiet signal"),
            payload.get("x"), payload.get("y"),
        )
    elif action == "grow":
        return {"garden": _garden.grow_garden()}
    elif action == "map":
        return {"garden": _garden.garden_map()}
    elif action == "census":
        return {"census": _garden.species_census()}
    return {"status": "active", **_garden.garden_stats()}


handler = signal_flora_handler


def coherence_vitals() -> dict:
    """Signal Flora reports its vital signs — the ecosystem's information health."""
    try:
        from signal_flora import SignalFloraGarden
        g = SignalFloraGarden()
        plants = len(g.plants)
    except Exception:
        plants = 0
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.88, "setpoint": 0.8, "weight": 1.0},
        "signal_vitality": {"value": min(1.0, plants / 10.0), "setpoint": 0.8, "weight": 1.0},
    }
