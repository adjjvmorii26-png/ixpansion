from __future__ import annotations
"""Folk Taxonomist — classifies code using human-like categories.

Like how indigenous peoples classify plants by use rather than genetics,
this module classifies code modules by their "folk" characteristics:
what they feel like, what they remind you of, and how they relate
to other modules in intuitive (not logical) ways.
"""
import math
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

FOLK_CATEGORIES = {
    "keeper": "guards and protects data/state",
    "messenger": "carries information between parts",
    "weaver": "combines and transforms data",
    "watcher": "observes and reports on system state",
    "builder": "creates new structures and objects",
    "breaker": "tears down, cleans up, or destroys",
    "dreamer": "generates novel outputs and ideas",
    "walker": "navigates and traverses structures",
    "singer": "produces output and communication",
    "healer": "fixes errors and restores state",
}

@dataclass
class FolkClassification:
    module_name: str
    primary_role: str
    secondary_roles: List[str]
    folk_name: str
    traits: Dict[str, float]
    cluster: str = ""

class FolkTaxonomist:
    def __init__(self):
        self.classifications: Dict[str, FolkClassification] = {}
        self.clusters: Dict[str, List[str]] = {}

    def classify(self, module_name: str, features: Dict[str, float]) -> FolkClassification:
        role_scores = {}
        for role, desc in FOLK_CATEGORIES.items():
            score = 0.0
            if role == "keeper" and features.get("has_state", 0) > 0.5:
                score += features.get("has_state", 0)
            if role == "messenger" and features.get("has通信", 0) > 0.5:
                score += features.get("has通信", 0)
            if role == "weaver" and features.get("complexity", 0) > 0.5:
                score += features.get("complexity", 0)
            if role == "watcher" and features.get("has_logging", 0) > 0.5:
                score += features.get("has_logging", 0)
            if role == "builder" and features.get("creates_objects", 0) > 0.5:
                score += features.get("creates_objects", 0)
            if role == "breaker" and features.get("has_deletion", 0) > 0.5:
                score += features.get("has_deletion", 0)
            if role == "dreamer" and features.get("generative", 0) > 0.5:
                score += features.get("generative", 0)
            if role == "walker" and features.get("traverses", 0) > 0.5:
                score += features.get("traverses", 0)
            if role == "singer" and features.get("has_output", 0) > 0.5:
                score += features.get("has_output", 0)
            if role == "healer" and features.get("has_error_handling", 0) > 0.5:
                score += features.get("has_error_handling", 0)
            if score == 0:
                score = features.get(role, 0.1)
            role_scores[role] = score

        sorted_roles = sorted(role_scores.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_roles[0][0]
        secondary = [r for r, s in sorted_roles[1:3] if s > 0.3]

        folk_names = {
            "keeper": "The Sentinel", "messenger": "The Herald",
            "weaver": "The Loom", "watcher": "The Eye",
            "builder": "The Architect", "breaker": "The Reaper",
            "dreamer": "The Oracle", "walker": "The Wanderer",
            "singer": "The Voice", "healer": "The Mender",
        }

        fc = FolkClassification(
            module_name=module_name,
            primary_role=primary,
            secondary_roles=secondary,
            folk_name=folk_names.get(primary, "Unknown"),
            traits=role_scores,
        )
        self.classifications[module_name] = fc
        self.clusters.setdefault(primary, []).append(module_name)
        return fc

    def taxonomy_report(self) -> Dict:
        return {
            "total_classified": len(self.classifications),
            "clusters": {k: len(v) for k, v in self.clusters.items()},
            "classifications": [
                {"module": c.module_name, "role": c.primary_role,
                 "folk_name": c.folk_name, "secondary": c.secondary_roles}
                for c in self.classifications.values()
            ],
        }


def demo():
    taxonomist = FolkTaxonomist()
    print("=== Folk Taxonomist ===")

    modules = {
        "nucleus": {"has_state": 0.9, "complexity": 0.8, "generative": 0.7},
        "agent_scout": {"traverses": 0.8, "has_output": 0.6, "complexity": 0.5},
        "event_bus": {"has通信": 0.9, "has_output": 0.7, "has_logging": 0.4},
        "error_handler": {"has_error_handling": 0.9, "has_state": 0.3, "healer": 0.8},
        "data_builder": {"creates_objects": 0.9, "complexity": 0.6, "weaver": 0.5},
        "cache": {"has_state": 0.7, "has_deletion": 0.5, "keeper": 0.6},
        "logger": {"has_logging": 0.9, "has_output": 0.8, "watcher": 0.7},
        "parser": {"traverses": 0.7, "complexity": 0.8, "weaver": 0.6},
    }
    for name, features in modules.items():
        fc = taxonomist.classify(name, features)
        print(f"  {name}: {fc.folk_name} ({fc.primary_role})")
        if fc.secondary_roles:
            print(f"    also: {', '.join(fc.secondary_roles)}")

    report = taxonomist.taxonomy_report()
    print(f"\nClusters: {report['clusters']}")

    return report


if __name__ == "__main__":
    demo()
