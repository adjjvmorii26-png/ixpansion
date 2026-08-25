"""Cosmic Ray Detector — Detects anomalous events in the codebase.

Simulates cosmic rays hitting the codebase, causing bit-flips and
corruptions that test the system's resilience.
"""
from __future__ import annotations
import hashlib
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CosmicRay:
    def __init__(self, energy: float, direction: tuple[float, float]):
        self.energy = energy
        self.direction = direction
        self.impacts: list[dict] = []


class CosmicRayDetector:
    def __init__(self, seed=42):
        self.seed = seed
        self.rng = random.Random(seed)
        self.rays: list[CosmicRay] = []
        self.impacts: list[dict] = []
        self.shield_strength = 1.0

    def emit_ray(self, energy: float = 1.0) -> CosmicRay:
        direction = (self.rng.uniform(-1, 1), self.rng.uniform(-1, 1))
        ray = CosmicRay(energy, direction)
        self.rays.append(ray)
        return ray

    def detect_impact(self, ray: CosmicRay, target_mass: float) -> dict:
        penetration = ray.energy * (1 - self.shield_strength * 0.5)
        damage = max(0, penetration - target_mass * 0.3)
        impact = {
            "energy": round(ray.energy, 4),
            "penetration": round(penetration, 4),
            "damage": round(damage, 4),
            "shielded": damage < 0.1,
        }
        self.impacts.append(impact)
        ray.impacts.append(impact)
        return impact

    def simulate(self, ray_count: int = 20):
        for _ in range(ray_count):
            energy = self.rng.expovariate(1.0)
            ray = self.emit_ray(min(5.0, energy))
            target_mass = self.rng.uniform(0.5, 3.0)
            self.detect_impact(ray, target_mass)
        total_damage = sum(i["damage"] for i in self.impacts)
        shielded = sum(1 for i in self.impacts if i["shielded"])
        return {
            "rays": ray_count, "impacts": len(self.impacts),
            "total_damage": round(total_damage, 4),
            "shielded": shielded, "shield_rate": round(shielded / max(1, len(self.impacts)), 4),
        }

    def report(self) -> dict:
        return {
            "detector": "cosmic_ray_detector",
            "rays": len(self.rays), "impacts": len(self.impacts),
            "shield_strength": self.shield_strength,
        }


def demo():
    detector = CosmicRayDetector(seed=42)
    sim = detector.simulate(ray_count=30)
    return {"simulation": sim, "report": detector.report()}


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
