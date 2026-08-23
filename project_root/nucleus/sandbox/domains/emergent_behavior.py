"""Emergent behavior — agents can mutate the rules of the sandbox itself.

When enough agents perform the same non-standard action repeatedly,
the action becomes a new rule of physics. The sandbox literally learns
from its inhabitants.
"""
from __future__ import annotations

import random
from collections import Counter
from dataclasses import dataclass, field
from typing import Any


@dataclass
class EmergentRule:
    rule_name: str
    trigger_action: str
    effect: str
    support_count: int      # How many agents performed this action
    threshold: int          # How many needed to codify
    codified: bool = False

    @property
    def progress(self) -> float:
        return min(1.0, self.support_count / max(self.threshold, 1))


class EmergentBehaviorDomain:
    CODIFICATION_THRESHOLD = 8  # Unique agents needed to make a rule real

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self._action_tracker: dict[str, set[str]] = {}  # action_name -> unique agent_ids
        self._codified_rules: dict[str, EmergentRule] = {}
        self._tick = 0

    def observe_action(self, agent_id: str, action_name: str,
                       effect_description: str = "") -> dict[str, Any]:
        """Record an unusual action; track whether it should become a rule."""
        if action_name not in self._action_tracker:
            self._action_tracker[action_name] = set()
        self._action_tracker[action_name].add(agent_id)

        supporters = len(self._action_tracker[action_name])

        # Check for codification
        if supporters >= self.CODIFICATION_THRESHOLD and action_name not in self._codified_rules:
            rule = EmergentRule(
                rule_name=f"rule_{action_name}",
                trigger_action=action_name,
                effect=effect_description or f"agents performing '{action_name}' alter reality",
                support_count=supporters,
                threshold=self.CODIFICATION_THRESHOLD,
                codified=True,
            )
            self._codified_rules[action_name] = rule
            return {"codified": True, "rule": rule.rule_name, "effect": rule.effect}

        return {"codified": False, "supporters": supporters,
                "progress": round(supporters / self.CODIFICATION_THRESHOLD, 3)}

    def is_rule_active(self, action_name: str) -> bool:
        return action_name in self._codified_rules

    @property
    def active_rules(self) -> list[dict[str, Any]]:
        return [
            {"rule": r.rule_name, "trigger": r.trigger_action,
             "effect": r.effect[:60], "supporters": r.support_count}
            for r in self._codified_rules.values()
        ]

    @property
    def pending_rules(self) -> list[dict[str, Any]]:
        return [
            {"action": action, "supporters": len(agents),
             "progress": round(len(agents) / self.CODIFICATION_THRESHOLD, 2)}
            for action, agents in self._action_tracker.items()
            if action not in self._codified_rules
        ]
