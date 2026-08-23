"""Self-bootstrapping creation logic — spawns new subsystems when needed."""
from __future__ import annotations

import hashlib
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Subsystem:
    name: str
    origin_trigger: str
    born_tick: int
    generation: int
    genome: dict[str, Any] = field(default_factory=dict)
    alive: bool = True

    @property
    def age_ticks(self) -> int:
        return self.born_tick  # Caller updates this externally if needed


class Autogenesis:
    def __init__(self) -> None:
        self._subsystems: dict[str, Subsystem] = {}
        self._spawn_rules: list[dict[str, Any]] = []
        self._tick = 0

    def add_spawn_rule(self, trigger: str, condition: callable,
                       genome_template: dict[str, Any]) -> None:
        """Register a rule that spawns a new subsystem when condition is met."""
        self._spawn_rules.append({
            "trigger": trigger,
            "condition": condition,
            "genome": genome_template,
            "last_fired": -1,
        })

    def tick(self, system_state: dict[str, Any]) -> list[Subsystem]:
        """Check all spawn rules; create new subsystems where triggered."""
        self._tick += 1
        spawned = []

        for rule in self._spawn_rules:
            if self._tick - rule["last_fired"] < 5:  # Cooldown
                continue
            if rule["condition"](system_state):
                name = f"{rule['trigger']}.{self._tick}"
                generation = max((s.generation for s in self._subsystems.values()), default=0) + 1
                sub = Subsystem(
                    name=name,
                    origin_trigger=rule["trigger"],
                    born_tick=self._tick,
                    generation=generation,
                    genome=dict(rule["genome"]),
                )
                self._subsystems[name] = sub
                spawned.append(sub)
                rule["last_fired"] = self._tick

        return spawned

    def cull(self, predicate: callable) -> int:
        """Remove subsystems matching a death condition."""
        to_remove = [name for name, s in self._subsystems.items() if predicate(s)]
        for name in to_remove:
            self._subsystems[name].alive = False
            del self._subsystems[name]
        return len(to_remove)

    @property
    def population(self) -> int:
        return len(self._subsystems)

    @property
    def lineage(self) -> dict[str, list[str]]:
        tree: dict[str, list[str]] = defaultdict(list)
        for s in self._subsystems.values():
            tree[s.origin_trigger].append(s.name)
        return dict(tree)

    @property
    def tick_count(self) -> int:
        return self._tick
