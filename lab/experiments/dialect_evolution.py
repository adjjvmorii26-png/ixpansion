#!/usr/bin/env python3
"""Dialect Evolution — how communication protocols mutate over time.

Bridges hex dialects (alpha, delta, omega) + linguistic_drift +
semantic_fossilization to model how communication protocols evolve.

Each generation, dialects undergo:
- Drift: random mutations in encoding rules
- Selection: successful dialects are preserved
- Fossilization: old dialects become read-only

This creates a fossil record of communication evolution — showing
how the system's language has changed over time.
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
class Dialect:
    dialect_id: str
    generation: int
    encoding_rules: dict[str, str]
    parent_id: str | None = None
    fitness: float = 1.0
    fossilized: bool = False

    def encode(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Encode a payload using this dialect's rules."""
        result = {}
        for key, value in payload.items():
            rule = self.encoding_rules.get(key, "passthrough")
            if rule == "uppercase":
                result[key] = str(value).upper() if isinstance(value, str) else value
            elif rule == "negate":
                result[key] = -value if isinstance(value, (int, float)) else value
            elif rule == "wrap":
                result[key] = f"[{value}]"
            elif rule == "hex_prefix":
                if isinstance(value, (int, float)):
                    result[key] = f"0x{int(value):x}"
                else:
                    result[key] = value
            elif rule == "timestamp":
                result[key] = f"ts:{value}"
            else:
                result[key] = value
        return result

    def payload(self) -> dict[str, Any]:
        return {
            "dialect_id": self.dialect_id,
            "generation": self.generation,
            "rules": dict(self.encoding_rules),
            "parent": self.parent_id,
            "fitness": round(self.fitness, 4),
            "fossilized": self.fossilized,
        }


@dataclass
class DialectEvolution:
    """Simulate the evolution of communication dialects."""
    mutation_rate: float = 0.2
    population_size: int = 5
    fossilize_threshold: int = 5
    seed: int | None = None

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)
        self._dialects: dict[str, Dialect] = {}
        self._fossil_record: list[Dialect] = []
        self._generation = 0
        self._evolution_log: list[dict[str, Any]] = []

    def create_alpha_dialect(self) -> Dialect:
        rules = {
            "value": "passthrough", "label": "uppercase",
            "count": "hex_prefix", "status": "passthrough",
        }
        d = Dialect(
            dialect_id=hashlib.sha256("alpha:0".encode()).hexdigest()[:12],
            generation=0, encoding_rules=rules,
        )
        self._dialects[d.dialect_id] = d
        return d

    def evolve(self) -> list[Dialect]:
        """Produce a new generation of dialects."""
        self._generation += 1
        new_dialects: list[Dialect] = []

        parents = [d for d in self._dialects.values() if not d.fossilized]
        if not parents:
            return []

        for _ in range(self.population_size):
            parent = self._rng.choice(parents)
            # Mutate encoding rules
            new_rules = dict(parent.encoding_rules)
            for key in list(new_rules.keys()):
                if self._rng.random() < self.mutation_rate:
                    new_rules[key] = self._rng.choice(
                        ["uppercase", "negate", "wrap", "hex_prefix", "timestamp", "passthrough"]
                    )

            # Add a new rule occasionally
            if self._rng.random() < 0.3:
                new_key = self._rng.choice(["entropy", "energy", "signal", "phase", "resonance"])
                new_rules[new_key] = self._rng.choice(
                    ["uppercase", "negate", "wrap", "hex_prefix", "timestamp", "passthrough"]
                )

            fid = hashlib.sha256(
                f"{parent.dialect_id}:{self._generation}:{self._rng.random()}".encode()
            ).hexdigest()[:12]

            # Fitness based on rule diversity and novelty
            unique_rules = len(set(new_rules.values()))
            novelty = sum(1 for k in new_rules if k not in parent.encoding_rules)
            fitness = unique_rules / 5.0 + novelty * 0.1

            child = Dialect(
                dialect_id=fid,
                generation=self._generation,
                encoding_rules=new_rules,
                parent_id=parent.dialect_id,
                fitness=fitness,
            )
            new_dialects.append(child)
            self._dialects[child.dialect_id] = child

        # Fossilize old dialects
        for d in list(self._dialects.values()):
            if not d.fossilized and self._generation - d.generation >= self.fossilize_threshold:
                d.fossilized = True
                self._fossil_record.append(d)

        # Selection: keep best, remove worst
        all_active = [d for d in self._dialects.values() if not d.fossilized]
        all_active.sort(key=lambda d: -d.fitness)
        keep = all_active[:self.population_size]
        remove = set(d.dialect_id for d in all_active) - set(d.dialect_id for d in keep)
        for rid in remove:
            del self._dialects[rid]

        self._evolution_log.append({
            "generation": self._generation,
            "new_dialects": len(new_dialects),
            "fossilized": sum(1 for d in self._dialects.values() if d.fossilized),
            "active": len(self._dialects),
        })

        return new_dialects

    def evolution_report(self) -> dict[str, Any]:
        active = [d for d in self._dialects.values() if not d.fossilized]
        return {
            "generation": self._generation,
            "active_dialects": len(active),
            "fossilized": len(self._fossil_record),
            "best_fitness": max((d.fitness for d in active), default=0),
            "avg_fitness": round(
                sum(d.fitness for d in active) / max(1, len(active)), 4
            ),
            "rule_diversity": len(set(
                rule for d in active for rule in d.encoding_rules.values()
            )),
            "log": self._evolution_log[-5:],
        }


def demo() -> dict[str, Any]:
    evo = DialectEvolution(seed=42, population_size=4)
    evo.create_alpha_dialect()
    for _ in range(8):
        evo.evolve()
    return evo.evolution_report()


def main() -> None:
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
