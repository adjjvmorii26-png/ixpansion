#!/usr/bin/env python3
"""Expansion Rule Synthesizer — generate new system rules from seed patterns.

Bridges rule_engine + mutation_applier + seeds_loader to create a
meta-rule system that generates new rules from existing ones. Given
a set of seed rules, the synthesizer applies transformations:
- Inversion (flip conditions)
- Composition (combine two rules)
- Abstraction (generalize specific rules)
- Mutation (randomly alter thresholds)

The result is a rule tree showing how complex rules emerge from simple seeds.
"""
from __future__ import annotations
from collections import Counter, defaultdict

import hashlib
import json
import math
import random
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Rule:
    rule_id: str
    name: str
    condition: str
    action: str
    strength: float = 1.0
    generation: int = 0
    parent_ids: tuple[str, ...] = ()
    transformation: str = "seed"

    def payload(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "condition": self.condition,
            "action": self.action,
            "strength": round(self.strength, 4),
            "generation": self.generation,
            "parent_ids": list(self.parent_ids),
            "transformation": self.transformation,
        }


def _rule_id(name: str, gen: int) -> str:
    raw = f"{name}:{gen}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


@dataclass
class RuleSynthesizer:
    """Generate new rules from seed patterns."""
    seed: int | None = None

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)
        self._rules: dict[str, Rule] = {}
        self._generation = 0

    def load_seeds(self, seeds: list[dict[str, str]]) -> list[Rule]:
        rules = []
        for seed in seeds:
            rule = Rule(
                rule_id=_rule_id(seed["name"], 0),
                name=seed["name"],
                condition=seed["condition"],
                action=seed["action"],
                strength=1.0,
                generation=0,
                transformation="seed",
            )
            self._rules[rule.rule_id] = rule
            rules.append(rule)
        return rules

    def invert(self, rule: Rule) -> Rule:
        """Flip the condition of a rule."""
        inversions = [
            ("above", "below"),
            ("greater", "less"),
            ("always", "never"),
            ("contains", "excludes"),
        ]
        new_condition = rule.condition
        for old_key, new_val in inversions:
            if old_key in new_condition:
                new_condition = new_condition.replace(old_key, new_val)
                break
        self._generation += 1
        new_rule = Rule(
            rule_id=_rule_id(f"inv_{rule.name}", self._generation),
            name=f"inverted_{rule.name}",
            condition=new_condition,
            action=rule.action,
            strength=rule.strength * 0.8,
            generation=self._generation,
            parent_ids=(rule.rule_id,),
            transformation="inversion",
        )
        self._rules[new_rule.rule_id] = new_rule
        return new_rule

    def compose(self, rule_a: Rule, rule_b: Rule) -> Rule:
        """Combine two rules into a compound rule."""
        self._generation += 1
        new_rule = Rule(
            rule_id=_rule_id(f"comp_{rule_a.name}_{rule_b.name}", self._generation),
            name=f"composed_{rule_a.name}_{rule_b.name}",
            condition=f"({rule_a.condition}) AND ({rule_b.condition})",
            action=f"{rule_a.action} then {rule_b.action}",
            strength=(rule_a.strength + rule_b.strength) / 2,
            generation=self._generation,
            parent_ids=(rule_a.rule_id, rule_b.rule_id),
            transformation="composition",
        )
        self._rules[new_rule.rule_id] = new_rule
        return new_rule

    def abstract(self, rule: Rule) -> Rule:
        """Generalize a specific rule."""
        self._generation += 1
        abstracted_condition = rule.condition.replace("0.5", "THRESHOLD")
        abstracted_condition = abstracted_condition.replace("10", "LIMIT")
        new_rule = Rule(
            rule_id=_rule_id(f"abs_{rule.name}", self._generation),
            name=f"abstract_{rule.name}",
            condition=abstracted_condition,
            action=rule.action,
            strength=rule.strength * 1.1,
            generation=self._generation,
            parent_ids=(rule.rule_id,),
            transformation="abstraction",
        )
        self._rules[new_rule.rule_id] = new_rule
        return new_rule

    def mutate(self, rule: Rule) -> Rule:
        """Randomly alter a rule's parameters."""
        self._generation += 1
        mutations = [
            lambda c: c.replace("0.5", f"{self._rng.uniform(0.1, 0.9):.2f}"),
            lambda c: c + " (with_noise)",
            lambda c: c.replace("AND", "OR"),
        ]
        mutate_fn = self._rng.choice(mutations)
        new_condition = mutate_fn(rule.condition)
        new_rule = Rule(
            rule_id=_rule_id(f"mut_{rule.name}", self._generation),
            name=f"mutant_{rule.name}",
            condition=new_condition,
            action=rule.action,
            strength=max(0.1, rule.strength + self._rng.uniform(-0.2, 0.2)),
            generation=self._generation,
            parent_ids=(rule.rule_id,),
            transformation="mutation",
        )
        self._rules[new_rule.rule_id] = new_rule
        return new_rule

    def synthesize_generation(self, parent_rules: list[Rule]) -> list[Rule]:
        """Produce a new generation from parent rules."""
        new_rules: list[Rule] = []

        # Invert each parent
        for rule in parent_rules:
            if self._rng.random() < 0.5:
                new_rules.append(self.invert(rule))

        # Compose random pairs
        if len(parent_rules) >= 2:
            for _ in range(min(3, len(parent_rules) // 2)):
                a = self._rng.choice(parent_rules)
                b = self._rng.choice(parent_rules)
                if a.rule_id != b.rule_id:
                    new_rules.append(self.compose(a, b))

        # Abstract one
        if parent_rules:
            new_rules.append(self.abstract(self._rng.choice(parent_rules)))

        # Mutate some
        for rule in parent_rules:
            if self._rng.random() < 0.3:
                new_rules.append(self.mutate(rule))

        return new_rules

    def rule_tree(self) -> dict[str, Any]:
        gens: dict[int, list[dict]] = defaultdict(list)
        for rule in self._rules.values():
            gens[rule.generation].append(rule.payload())

        return {
            "total_rules": len(self._rules),
            "generations": {g: rules for g, rules in sorted(gens.items())},
            "transformations": dict(Counter(
                r.transformation for r in self._rules.values()
            )),
        }




def demo() -> dict[str, Any]:
    synth = RuleSynthesizer(seed=42)

    seeds = [
        {"name": "entropy_check", "condition": "entropy above 0.5", "action": "inject_order"},
        {"name": "agent_bound", "condition": "agent_count less 10", "action": "spawn_new"},
        {"name": "resource_low", "condition": "resource below 0.3", "action": "alert_system"},
    ]

    gen0 = synth.load_seeds(seeds)
    gen1 = synth.synthesize_generation(gen0)
    gen2 = synth.synthesize_generation(gen1)

    return synth.rule_tree()


def main() -> None:
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
