from __future__ import annotations
"""Negative Space Analyzer — reads what's absent as evidence.

Inspired by solid-organism's negative_space module, this analyzes the
gaps, missing connections, and absent modules in the system. What's
NOT there can be as revealing as what IS there — absences reveal design
decisions, abandoned paths, and hidden opportunities.
"""
import math
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

@dataclass
class Absence:
    name: str
    absence_type: str
    surrounding_evidence: List[str]
    pressure: float
    interpretation: str

class NegativeSpaceAnalyzer:
    def __init__(self):
        self.present: Set[str] = set()
        self.expected: Set[str] = set()
        self.dependencies: Dict[str, Set[str]] = {}
        self.absences: List[Absence] = []

    def register_present(self, name: str, dependencies: List[str] = None):
        self.present.add(name)
        self.dependencies[name] = set(dependencies or [])

    def register_expected(self, name: str):
        self.expected.add(name)

    def analyze(self) -> List[Absence]:
        self.absences.clear()
        missing = self.expected - self.present
        for name in missing:
            connections_to = sum(1 for deps in self.dependencies.values() if name in deps)
            connections_from = len(self.dependencies.get(name, set()))
            total_connections = connections_to + connections_from
            surrounding = []
            for mod, deps in self.dependencies.items():
                if name in deps:
                    surrounding.append(f"depended_on_by:{mod}")
            pressure = min(1.0, total_connections * 0.2 + connections_to * 0.3)
            if pressure > 0.5:
                interpretation = "critical_gap"
            elif pressure > 0.2:
                interpretation = "notable_absence"
            else:
                interpretation = "minor_gap"
            self.absences.append(Absence(
                name=name, absence_type="missing_module",
                surrounding_evidence=surrounding,
                pressure=round(pressure, 3),
                interpretation=interpretation,
            ))
        return self.absences

    def empty_connections(self) -> List[Dict]:
        empty = []
        for mod, deps in self.dependencies.items():
            for dep in deps:
                if dep not in self.present:
                    empty.append({"module": mod, "missing_dependency": dep})
        return empty

    def report(self) -> Dict:
        self.analyze()
        return {
            "present": len(self.present),
            "expected": len(self.expected),
            "absent": len(self.absences),
            "empty_connections": len(self.empty_connections()),
            "critical_gaps": sum(1 for a in self.absences if a.interpretation == "critical_gap"),
            "absences": [
                {"name": a.name, "pressure": a.pressure,
                 "interpretation": a.interpretation}
                for a in self.absences
            ],
        }


def demo():
    analyzer = NegativeSpaceAnalyzer()
    print("=== Negative Space Analyzer ===")
    analyzer.register_present("nucleus", ["kernel", "state"])
    analyzer.register_present("agent", ["nucleus", "sandbox"])
    analyzer.register_present("sandbox", ["nucleus"])
    analyzer.register_expected("nucleus")
    analyzer.register_expected("agent")
    analyzer.register_expected("sandbox")
    analyzer.register_expected("protocol")
    analyzer.register_expected("logger")
    analyzer.register_expected("cache")
    report = analyzer.report()
    print(f"  Present: {report['present']}, Expected: {report['expected']}")
    print(f"  Absent: {report['absent']}")
    print(f"  Critical gaps: {report['critical_gaps']}")
    print(f"  Empty connections: {report['empty_connections']}")
    print("  Absences:")
    for a in report["absences"]:
        print(f"    {a['name']}: {a['interpretation']} (pressure={a['pressure']})")
    return report


if __name__ == "__main__":
    demo()
