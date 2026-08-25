from __future__ import annotations
"""Myth Generator — creates origin myths for modules from their history.

Like ancient peoples who explained natural phenomena through mythology,
this module creates narrative origin stories for code modules based on
their git history, dependencies, complexity, and naming patterns.
"""
import math
import hashlib
import json
import random
from dataclasses import dataclass, field
from typing import Dict, List

ARCHETYPES = ["hero", "trickster", "sage", "creator", "destroyer", "guardian"]
SETTINGS = ["the ancient void", "the digital wilderness", "the silicon mountains",
            "the quantum forest", "the binary seas", "the circuit plains"]
CONFLICTS = ["the great refactoring", "the dependency war", "the merge conflict",
             "the memory leak flood", "the infinite loop curse", "the null pointer plague"]
RESOLUTIONS = ["found peace through abstraction", "unified the warring interfaces",
               "discovered the sacred algorithm", "wove the threads of concurrency",
               "decoded the ancient bytecode", "built a bridge across the divide"]

@dataclass
class Myth:
    module_name: str
    archetype: str
    setting: str
    conflict: str
    resolution: str
    narrative: str
    generation: int = 0

class MythGenerator:
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.myths: Dict[str, Myth] = {}

    def _module_archetype(self, name: str) -> str:
        h = int(hashlib.md5(name.encode()).hexdigest()[:8], 16)
        return ARCHETYPES[h % len(ARCHETYPES)]

    def _generate_narrative(self, myth: Myth) -> str:
        return (
            f"In {myth.setting}, there arose a module called {myth.module_name}, "
            f"a {myth.archetype} among the digital beings. "
            f"But {myth.conflict} threatened all that was known. "
            f"Through trials and tribulations, {myth.module_name} "
            f"{myth.resolution}, and thus its legend was born."
        )

    def generate(self, module_name: str, extra_traits: Dict = None) -> Myth:
        archetype = self._module_archetype(module_name)
        setting = self.rng.choice(SETTINGS)
        conflict = self.rng.choice(CONFLICTS)
        resolution = self.rng.choice(RESOLUTIONS)

        myth = Myth(
            module_name=module_name, archetype=archetype,
            setting=setting, conflict=conflict,
            resolution=resolution, narrative="",
        )
        myth.narrative = self._generate_narrative(myth)
        self.myths[module_name] = myth
        return myth

    def pantheon(self) -> Dict[str, str]:
        return {name: myth.archetype for name, myth in self.myths.items()}

    def myth_report(self) -> Dict:
        archetype_counts = {}
        for myth in self.myths.values():
            archetype_counts[myth.archetype] = archetype_counts.get(myth.archetype, 0) + 1
        return {
            "total_myths": len(self.myths),
            "archetype_distribution": archetype_counts,
            "myths": [
                {"module": m.module_name, "archetype": m.archetype,
                 "setting": m.setting}
                for m in self.myths.values()
            ],
        }


def demo():
    generator = MythGenerator(seed=42)
    print("=== Myth Generator ===")

    modules = ["nucleus", "hex_vm", "agent_scout", "sandbox",
               "pipeline", "observer", "meme_engine", "crystal"]
    for name in modules:
        myth = generator.generate(name)
        print(f"\n  {name} ({myth.archetype}):")
        print(f"    {myth.narrative[:120]}...")

    print(f"\nPantheon: {generator.pantheon()}")
    report = generator.myth_report()
    print(f"Archetypes: {report['archetype_distribution']}")

    return report


if __name__ == "__main__":
    demo()
