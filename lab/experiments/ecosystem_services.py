from __future__ import annotations
"""Ecosystem Services — quantifies what each module provides to the system.

Like natural ecosystem services (clean air, water filtration, pollination),
code modules provide services: data processing, error handling, caching,
logging. This module measures and values those services.
"""
import math
import json
from dataclasses import dataclass, field
from typing import Dict, List

SERVICE_TYPES = {
    "data_processing": 1.0,
    "error_handling": 0.8,
    "caching": 0.7,
    "logging": 0.6,
    "authentication": 0.9,
    "serialization": 0.5,
    "monitoring": 0.7,
    "routing": 0.6,
}

@dataclass
class ServiceProfile:
    module: str
    services: Dict[str, float]
    total_value: float = 0.0
    uniqueness: float = 0.0

class EcosystemServices:
    def __init__(self):
        self.profiles: Dict[str, ServiceProfile] = {}

    def register(self, module: str, services: Dict[str, float]):
        total = sum(services.get(s, 0) * v for s, v in SERVICE_TYPES.items())
        self.profiles[module] = ServiceProfile(
            module=module, services=services, total_value=total,
        )

    def assess(self):
        all_services = set()
        for p in self.profiles.values():
            all_services.update(p.services.keys())
        for module, profile in self.profiles.items():
            provided = set(profile.services.keys())
            others = set()
            for m, p in self.profiles.items():
                if m != module:
                    others.update(p.services.keys())
            unique = provided - others
            profile.uniqueness = len(unique) / max(len(all_services), 1)

    def ranking(self) -> List[Dict]:
        self.assess()
        return sorted([
            {"module": p.module, "value": round(p.total_value, 3),
             "uniqueness": round(p.uniqueness, 3),
             "services": list(p.services.keys())}
            for p in self.profiles.values()
        ], key=lambda x: x["value"], reverse=True)


def demo():
    eco = EcosystemServices()
    print("=== Ecosystem Services ===")
    eco.register("nucleus", {"data_processing": 0.9, "routing": 0.7})
    eco.register("agent", {"data_processing": 0.5, "monitoring": 0.6})
    eco.register("sandbox", {"caching": 0.8, "data_processing": 0.4})
    eco.register("auth_module", {"authentication": 0.95})
    eco.register("logger", {"logging": 0.9, "monitoring": 0.3})
    ranking = eco.ranking()
    for r in ranking:
        print(f"  {r['module']}: value={r['value']}, "
              f"uniqueness={r['uniqueness']}, services={r['services']}")
    return {"ranking": ranking}


if __name__ == "__main__":
    demo()
