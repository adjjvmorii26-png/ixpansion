from __future__ import annotations
"""Invasive Species Detector — finds modules spreading aggressively.

Like invasive species that outcompete native ones, some modules grow
unchecked, consuming resources and displacing others. This detector
identifies them by measuring growth rate, resource consumption, and
territory expansion.
"""
import math
import json
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class SpeciesProfile:
    name: str
    file_count: int = 0
    line_count: int = 0
    import_count: int = 0
    growth_rate: float = 0.0
    resource_consumption: float = 0.0
    territory: float = 0.0
    invasiveness_score: float = 0.0

class InvasiveSpeciesDetector:
    def __init__(self):
        self.profiles: Dict[str, SpeciesProfile] = {}
        self.baseline: Dict[str, float] = {}

    def register(self, name: str, file_count: int, line_count: int,
                 import_count: int):
        self.profiles[name] = SpeciesProfile(
            name=name, file_count=file_count,
            line_count=line_count, import_count=import_count,
        )

    def set_baseline(self, name: str, historical_lines: float):
        self.baseline[name] = historical_lines

    def detect(self, growth_threshold: float = 0.5) -> List[SpeciesProfile]:
        invasive = []
        for name, profile in self.profiles.items():
            base = self.baseline.get(name, profile.line_count)
            profile.growth_rate = (profile.line_count - base) / max(base, 1)
            profile.resource_consumption = profile.import_count / max(profile.file_count, 1)
            profile.territory = profile.file_count / max(len(self.profiles), 1)
            profile.invasiveness_score = (
                min(1.0, max(0, profile.growth_rate)) * 0.4 +
                min(1.0, profile.resource_consumption * 0.2) * 0.3 +
                profile.territory * 0.3
            )
            if profile.invasiveness_score > growth_threshold:
                invasive.append(profile)
        return sorted(invasive, key=lambda p: p.invasiveness_score, reverse=True)

    def report(self) -> Dict:
        all_profiles = list(self.profiles.values())
        return {
            "total_modules": len(all_profiles),
            "invasive_count": sum(1 for p in all_profiles if p.invasiveness_score > 0.5),
            "avg_invasiveness": sum(p.invasiveness_score for p in all_profiles) / max(len(all_profiles), 1),
        }


def demo():
    detector = InvasiveSpeciesDetector()
    print("=== Invasive Species Detector ===")
    detector.register("nucleus", 3, 500, 20)
    detector.register("agent", 8, 1200, 45)
    detector.register("sandbox", 4, 600, 15)
    detector.register("rogue_module", 15, 3000, 80)
    detector.set_baseline("nucleus", 400)
    detector.set_baseline("agent", 500)
    detector.set_baseline("sandbox", 500)
    detector.set_baseline("rogue_module", 200)
    invasive = detector.detect()
    print(f"  Invasive species found: {len(invasive)}")
    for sp in invasive:
        print(f"    {sp.name}: score={sp.invasiveness_score:.3f}, "
              f"growth={sp.growth_rate:.1%}, files={sp.file_count}")
    return detector.report()


if __name__ == "__main__":
    demo()
