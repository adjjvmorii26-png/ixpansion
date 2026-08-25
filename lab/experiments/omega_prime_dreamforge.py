#!/usr/bin/env python3
"""Omega Prime Dreamforge — the repo dreams new subsystems.

A generative engine that synthesizes new module concepts by finding
latent patterns across all existing modules. It:
1. Profiles every module's characteristics (entropy, novelty, connectivity)
2. Finds "dream gaps" — combinations of traits that don't exist yet
3. Generates new module blueprints from these gaps
4. Rates each blueprint for feasibility and innovation

This is the repo's imagination — it creates the modules that
could exist but don't yet.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ModuleBlueprint:
    blueprint_id: str
    name: str
    description: str
    traits: dict[str, float]
    inspiration_sources: list[str]
    feasibility: float
    innovation: float

    @property
    def viability_score(self) -> float:
        return round(self.feasibility * 0.6 + self.innovation * 0.4, 4)

    def payload(self) -> dict[str, Any]:
        return {
            "blueprint_id": self.blueprint_id,
            "name": self.name,
            "description": self.description,
            "traits": {k: round(v, 3) if isinstance(v, (int, float)) else v for k, v in self.traits.items()},
            "inspiration": self.inspiration_sources,
            "feasibility": round(self.feasibility, 3),
            "innovation": round(self.innovation, 3),
            "viability": self.viability_score,
        }


@dataclass
class ModuleProfile:
    name: str
    traits: dict[str, float]
    connections: list[str] = field(default_factory=list)


TRAIT_NAMES = [
    "entropy", "novelty", "connectivity", "depth",
    "speed", "safety", "chaos", "order",
    "memory", "perception", "generation", "resilience",
]

DESCRIPTION_TEMPLATES = [
    "A {adj1} system for {noun1} that bridges {noun2} and {noun3}",
    "An adaptive {noun1} engine with {adj2} {noun2} capabilities",
    "A {adj1} framework for {noun1} through {noun2} analysis",
    "A self-organizing {noun1} network with {adj2} {noun2} dynamics",
    "A {adj1} {noun1} simulator that models {noun2} and {noun3}",
]

NOUNS = [
    "signal propagation", "temporal dynamics", "spatial reasoning",
    "consensus formation", "resource allocation", "boundary detection",
    "pattern recognition", "entropy management", "state evolution",
    "network topology", "behavioral mutation", "memory consolidation",
    "decision arbitrage", "constraint relaxation", "phase transition",
]

ADJECTIVES = [
    "recursive", "adaptive", "stochastic", "deterministic",
    "self-similar", "entropic", "crystalline", "mycelial",
    "fractal", "quantum", "topological", "resonant",
]


@dataclass
class OmegaDreamforge:
    """Generate new module blueprints from latent patterns."""
    seed: int | None = None

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)
        self._profiles: dict[str, ModuleProfile] = {}
        self._blueprints: list[ModuleBlueprint] = []
        self._dream_log: list[dict[str, Any]] = []

    def register_module(self, name: str, traits: dict[str, float],
                        connections: list[str] | None = None) -> None:
        self._profiles[name] = ModuleProfile(
            name=name, traits=traits, connections=connections or [],
        )

    def find_dream_gaps(self) -> list[dict[str, Any]]:
        """Find trait combinations that don't exist in any module."""
        if not self._profiles:
            return []

        # Compute trait space coverage
        trait_coverage: dict[str, list[float]] = defaultdict(list)
        for profile in self._profiles.values():
            for trait, value in profile.traits.items():
                trait_coverage[trait].append(value)

        # Find underrepresented trait regions
        gaps: list[dict[str, Any]] = []
        for trait in TRAIT_NAMES:
            values = trait_coverage.get(trait, [])
            if not values:
                gaps.append({"trait": trait, "gap_type": "absent", "suggestion": 0.5})
                continue
            mean_val = sum(values) / len(values)
            if mean_val < 0.3:
                gaps.append({"trait": trait, "gap_type": "underrepresented_high", "suggestion": 0.7})
            elif mean_val > 0.7:
                gaps.append({"trait": trait, "gap_type": "underrepresented_low", "suggestion": 0.3})

        # Find disconnected trait pairs
        all_connections = set()
        for profile in self._profiles.values():
            for conn in profile.connections:
                all_connections.add(conn)

        disconnected = [
            name for name in self._profiles
            if name not in all_connections and not self._profiles[name].connections
        ]
        for name in disconnected[:3]:
            gaps.append({"trait": "connectivity", "gap_type": "isolated_module",
                        "module": name, "suggestion": "connect"})

        return gaps

    def dream(self, count: int = 3) -> list[ModuleBlueprint]:
        """Generate new module blueprints from dream gaps."""
        gaps = self.find_dream_gaps()
        profiles = list(self._profiles.values())

        new_blueprints: list[ModuleBlueprint] = []
        for _ in range(count):
            # Randomly combine traits from different modules
            if len(profiles) >= 2:
                parent_a = self._rng.choice(profiles)
                parent_b = self._rng.choice(profiles)
                sources = [parent_a.name, parent_b.name]

                # Blend traits
                blended: dict[str, float] = {}
                all_traits = set(parent_a.traits) | set(parent_b.traits)
                for trait in all_traits:
                    va = parent_a.traits.get(trait, 0.5)
                    vb = parent_b.traits.get(trait, 0.5)
                    alpha = self._rng.uniform(0.3, 0.7)
                    blended[trait] = round(alpha * va + (1 - alpha) * vb, 3)

                # Add a novel trait from gaps
                if gaps:
                    gap = self._rng.choice(gaps)
                    blended[gap["trait"]] = gap.get("suggestion", 0.5)
            else:
                sources = ["seed"]
                blended = {t: self._rng.uniform(0.0, 1.0) for t in TRAIT_NAMES}

            # Generate name and description
            adj1 = self._rng.choice(ADJECTIVES)
            adj2 = self._rng.choice(ADJECTIVES)
            noun1 = self._rng.choice(NOUNS)
            noun2 = self._rng.choice(NOUNS)
            noun3 = self._rng.choice(NOUNS)
            name = f"{adj1}_{noun1.split()[0]}_{self._rng.randint(100, 999)}"
            template = self._rng.choice(DESCRIPTION_TEMPLATES)
            description = template.format(adj1=adj1, adj2=adj2, noun1=noun1, noun2=noun2, noun3=noun3)

            # Rate feasibility and innovation
            trait_diversity = len(set(blended.values())) / max(1, len(blended))
            novelty = sum(1 for t in blended if isinstance(blended[t], (int, float)) and (blended[t] > 0.7 or blended[t] < 0.3)) / max(1, len(blended))
            feasibility = max(0.2, min(1.0, trait_diversity * 0.5 + 0.3))
            innovation = max(0.1, min(1.0, novelty * 0.6 + len(sources) * 0.1))

            bid = hashlib.sha256(
                f"{name}:{json.dumps(blended, sort_keys=True)}".encode()
            ).hexdigest()[:12]

            blueprint = ModuleBlueprint(
                blueprint_id=bid,
                name=name,
                description=description,
                traits=blended,
                inspiration_sources=sources,
                feasibility=feasibility,
                innovation=innovation,
            )
            new_blueprints.append(blueprint)
            self._blueprints.append(blueprint)

        self._dream_log.append({
            "blueprints_generated": len(new_blueprints),
            "gaps_found": len(gaps),
            "avg_viability": round(
                sum(b.viability_score for b in new_blueprints) / max(1, len(new_blueprints)), 3
            ),
        })

        return new_blueprints

    def dream_report(self) -> dict[str, Any]:
        if not self._blueprints:
            return {"status": "no_dreams_yet"}

        viability_scores = [b.viability_score for b in self._blueprints]
        return {
            "total_blueprints": len(self._blueprints),
            "mean_viability": round(sum(viability_scores) / len(viability_scores), 4),
            "top_blueprints": [
                b.payload() for b in sorted(self._blueprints, key=lambda x: -x.viability_score)[:3]
            ],
            "dream_log": self._dream_log[-3:],
        }


def demo() -> dict[str, Any]:
    forge = OmegaDreamforge(seed=42)

    # Register existing modules with their trait profiles
    modules = {
        "spectral_drift": {"entropy": 0.3, "novelty": 0.8, "memory": 0.6, "perception": 0.4},
        "temporal_resonance": {"entropy": 0.2, "speed": 0.7, "memory": 0.5, "generation": 0.3},
        "cross_pollinator": {"connectivity": 0.9, "novelty": 0.7, "chaos": 0.4, "order": 0.3},
        "memory_palace": {"memory": 0.9, "depth": 0.6, "resilience": 0.5, "perception": 0.7},
        "neural_topology": {"connectivity": 0.8, "depth": 0.7, "generation": 0.6, "safety": 0.4},
        "mood_synesthesia": {"novelty": 0.9, "perception": 0.8, "chaos": 0.5, "generation": 0.4},
        "glitch_generator": {"chaos": 0.9, "entropy": 0.8, "novelty": 0.6, "speed": 0.5},
        "quantum_tunneling": {"resilience": 0.7, "depth": 0.5, "connectivity": 0.4, "safety": 0.6},
    }

    for name, traits in modules.items():
        forge.register_module(name, traits)

    # Find gaps and dream
    gaps = forge.find_dream_gaps()
    blueprints = forge.dream(count=5)

    return {
        "gaps_found": len(gaps),
        "sample_gaps": gaps[:3],
        "report": forge.dream_report(),
    }


def main() -> None:
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
