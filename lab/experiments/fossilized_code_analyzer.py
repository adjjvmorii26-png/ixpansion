from __future__ import annotations
"""Fossilized Code Analyzer — reconstructs evolutionary history of dead code.

Like paleontologists reconstructing extinct species from fossils, this
module analyzes "dead code" remnants, orphaned functions, and deprecated
modules to reconstruct the evolutionary timeline of how the codebase
changed, what went extinct, and why.
"""
import math
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum

class CodeFossilType(Enum):
    ORPHAN_FUNCTION = "orphan_function"
    DEPRECATED_MODULE = "deprecated_module"
    DEAD_IMPORT = "dead_import"
    GHOST_CLASS = "ghost_class"
    FOSSIL_CONFIG = "fossil_config"
    EXTINCT_TEST = "extinct_test"

@dataclass
class CodeFossil:
    name: str
    fossil_type: CodeFossilType
    era: str
    complexity: float
    dependencies: Set[str] = field(default_factory=set)
    estimated_age: int = 0
    last_seen: str = "unknown"
    cause_of_death: str = "unknown"
    confidence: float = 0.0

@dataclass
class EvolutionaryEra:
    name: str
    start_tick: int
    end_tick: int
    dominant_species: List[str]
    extinction_events: int
    innovations: List[str]

@dataclass
class FossilRecord:
    fossils: List[CodeFossil]
    eras: List[EvolutionaryEra]
    total_extinct: int
    survival_rate: float
    complexity_trend: List[float]

class FossilizedCodeAnalyzer:
    def __init__(self):
        self.fossils: List[CodeFossil] = []
        self.eras: List[EvolutionaryEra] = []
        self.timeline: List[Dict] = []
        self.tick = 0

    def _estimate_era(self, complexity: float) -> str:
        if complexity > 0.8:
            return "precambrian"
        elif complexity > 0.5:
            return "paleozoic"
        elif complexity > 0.3:
            return "mesozoic"
        return "cenozoic"

    def _cause_of_death(self, fossil: CodeFossil) -> str:
        if fossil.complexity > 0.7:
            return "complexity_collapse"
        elif len(fossil.dependencies) > 5:
            return "dependency_cascade"
        elif fossil.fossil_type == CodeFossilType.ORPHAN_FUNCTION:
            return "isolation"
        elif fossil.fossil_type == CodeFossilType.DEAD_IMPORT:
            return "refactor_obsolescence"
        return "natural_selection"

    def register_fossil(self, name: str, fossil_type: CodeFossilType,
                       complexity: float, dependencies: List[str] = None,
                       estimated_age: int = 0) -> CodeFossil:
        fossil = CodeFossil(
            name=name, fossil_type=fossil_type,
            era=self._estimate_era(complexity),
            complexity=complexity,
            dependencies=set(dependencies or []),
            estimated_age=estimated_age,
        )
        fossil.cause_of_death = self._cause_of_death(fossil)
        fossil.confidence = min(1.0, 0.5 + complexity * 0.3 + estimated_age * 0.001)
        self.fossils.append(fossil)
        self.timeline.append({
            "tick": self.tick, "event": "fossil_registered",
            "name": name, "type": fossil_type.value,
        })
        return fossil

    def record_era(self, name: str, duration: int, species: List[str],
                   extinctions: int = 0, innovations: List[str] = None):
        era = EvolutionaryEra(
            name=name, start_tick=self.tick,
            end_tick=self.tick + duration,
            dominant_species=species,
            extinction_events=extinctions,
            innovations=innovations or [],
        )
        self.eras.append(era)
        self.tick += duration

    def analyze_lineage(self, name: str) -> Dict:
        related = [f for f in self.fossils
                   if name in f.dependencies or f.name.startswith(name.split("_")[0])]
        return {
            "fossil": name,
            "related_fossils": len(related),
            "lineage_depth": max((f.estimated_age for f in related), default=0),
            "extinction_causes": list(set(f.cause_of_death for f in related)),
        }

    def complexity_trend(self) -> List[float]:
        if not self.fossils:
            return []
        sorted_fossils = sorted(self.fossils, key=lambda f: f.estimated_age)
        return [f.complexity for f in sorted_fossils]

    def extinction_summary(self) -> Dict:
        causes = {}
        for f in self.fossils:
            causes[f.cause_of_death] = causes.get(f.cause_of_death, 0) + 1
        eras_extinctions = sum(e.extinction_events for e in self.eras)
        return {
            "total_fossils": len(self.fossils),
            "extinction_causes": causes,
            "era_extinctions": eras_extinctions,
            "avg_complexity": sum(f.complexity for f in self.fossils) / max(len(self.fossils), 1),
            "avg_confidence": sum(f.confidence for f in self.fossils) / max(len(self.fossils), 1),
        }

    def generate_report(self) -> Dict:
        return {
            "fossils": len(self.fossils),
            "eras": len(self.eras),
            "extinction_summary": self.extinction_summary(),
            "complexity_trend": self.complexity_trend(),
            "timeline_events": len(self.timeline),
            "dominant_era": self.eras[-1].name if self.eras else "unknown",
        }


def demo():
    analyzer = FossilizedCodeAnalyzer()
    print("=== Fossilized Code Analyzer ===")

    analyzer.record_era("primordial", 100, ["module_a", "module_b"], 2,
                        ["event_bus", "config_loader"])
    analyzer.record_era("expansion", 200, ["module_c", "module_d", "module_e"], 5,
                        ["hex_vm", "sandbox"])
    analyzer.record_era("consolidation", 150, ["module_f"], 1, ["pipeline"])

    fossils_data = [
        ("old_parser", CodeFossilType.ORPHAN_FUNCTION, 0.7, ["json"], 500),
        ("legacy_auth", CodeFossilType.DEPRECATED_MODULE, 0.9, ["crypto", "db"], 800),
        ("unused_helper", CodeFossilType.ORPHAN_FUNCTION, 0.3, [], 200),
        ("dead_event_bus", CodeFossilType.GHOST_CLASS, 0.6, ["asyncio"], 600),
        ("old_config", CodeFossilType.FOSSIL_CONFIG, 0.4, ["yaml"], 300),
        ("extinct_test", CodeFossilType.EXTINCT_TEST, 0.2, ["pytest"], 150),
        ("deprecated_api", CodeFossilType.DEAD_IMPORT, 0.8, ["flask", "sqlalchemy"], 700),
        ("ancient_utils", CodeFossilType.ORPHAN_FUNCTION, 0.5, ["math", "os"], 400),
    ]
    for name, ftype, complexity, deps, age in fossils_data:
        analyzer.register_fossil(name, ftype, complexity, deps, age)

    print(f"  Eras: {len(analyzer.eras)}")
    print(f"  Fossils: {len(analyzer.fossils)}")

    summary = analyzer.extinction_summary()
    print(f"\nExtinction summary:")
    print(f"  Total fossils: {summary['total_fossils']}")
    print(f"  Causes: {summary['extinction_causes']}")
    print(f"  Avg complexity: {summary['avg_complexity']:.3f}")

    lineage = analyzer.analyze_lineage("module_a")
    print(f"\nLineage of 'module_a': {lineage}")

    report = analyzer.generate_report()
    print(f"\nComplexity trend: {[round(c, 2) for c in report['complexity_trend']]}")

    return report


if __name__ == "__main__":
    demo()
