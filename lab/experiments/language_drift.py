from __future__ import annotations
"""Language Drift — models how API naming conventions evolve over time.

Names in codebases drift like languages — "fetch" becomes "get" becomes
"retrieve" becomes "obtain". This module tracks naming evolution across
versions and predicts future naming trends based on drift velocity.
"""
import math
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

@dataclass
class NameEvolution:
    original: str
    current: str
    versions: List[str]
    drift_velocity: float = 0.0
    stability: float = 1.0

@dataclass
class NamingConvention:
    domain: str
    preferred_style: str
    vocabulary: List[str]
    drift_direction: str = "stable"

class LanguageDriftTracker:
    def __init__(self):
        self.evolutions: Dict[str, NameEvolution] = {}
        self.conventions: List[NamingConvention] = []
        self.version = 0
        self.drift_log: List[Dict] = []

    def track(self, name: str, domain: str = "general") -> NameEvolution:
        evolution = NameEvolution(
            original=name, current=name,
            versions=[name],
        )
        self.evolutions[f"{domain}:{name}"] = evolution
        return evolution

    def evolve(self, name: str, domain: str = "general",
               new_name: Optional[str] = None):
        key = f"{domain}:{name}"
        if key not in self.evolutions:
            return
        evo = self.evolutions[key]
        if new_name is None:
            new_name = evo.current
            synonyms = {
                "get": ["fetch", "retrieve", "obtain", "acquire"],
                "set": ["put", "store", "save", "assign"],
                "check": ["validate", "verify", "confirm", "assert"],
                "run": ["execute", "process", "perform", "dispatch"],
                "send": ["transmit", "dispatch", "broadcast", "emit"],
            }
            for base, alts in synonyms.items():
                if evo.current.lower() in [base] + alts:
                    idx = alts.index(evo.current.lower()) if evo.current.lower() in alts else -1
                    new_name = alts[(idx + 1) % len(alts)]
                    break

        old_name = evo.current
        evo.current = new_name
        evo.versions.append(new_name)
        evo.drift_velocity = len(evo.versions) / max(1, self.version + 1)
        evo.stability = 1.0 / len(evo.versions)

        self.version += 1
        self.drift_log.append({
            "domain": domain, "from": old_name, "to": new_name,
            "version": self.version,
        })

    def drift_analysis(self) -> Dict:
        total_drift = sum(e.drift_velocity for e in self.evolutions.values())
        avg_stability = sum(e.stability for e in self.evolutions.values()) / max(len(self.evolutions), 1)
        return {
            "tracked_names": len(self.evolutions),
            "total_drift_events": len(self.drift_log),
            "total_drift_velocity": round(total_drift, 3),
            "avg_stability": round(avg_stability, 3),
            "evolutions": [
                {"original": e.original, "current": e.current,
                 "versions": len(e.versions), "stability": round(e.stability, 3)}
                for e in self.evolutions.values()
            ],
        }


def demo():
    tracker = LanguageDriftTracker()
    print("=== Language Drift Tracker ===")

    names = [
        ("fetch_data", "api"), ("validate_input", "core"),
        ("run_process", "engine"), ("send_message", "protocol"),
        ("check_status", "monitor"),
    ]
    for name, domain in names:
        tracker.track(name, domain)

    for _ in range(5):
        for name, domain in names:
            tracker.evolve(name, domain)

    analysis = tracker.drift_analysis()
    print(f"  Tracked: {analysis['tracked_names']} names")
    print(f"  Drift events: {analysis['total_drift_events']}")
    print(f"  Avg stability: {analysis['avg_stability']}")
    print("\nName evolutions:")
    for evo in analysis["evolutions"]:
        print(f"  {evo['original']} → {evo['current']} "
              f"({evo['versions']} versions, stability={evo['stability']})")

    return analysis


if __name__ == "__main__":
    demo()
