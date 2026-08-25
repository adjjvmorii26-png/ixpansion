#!/usr/bin/env python3
"""Glitch Pattern Generator — create and classify system anomalies.

Bridges conflict_resolver + identity_split + temporal_loop to generate
synthetic glitches, classify them by type, and predict their severity.

Glitch types:
- Identity split: same agent has contradictory states
- Temporal loop: action sequence repeats infinitely
- Rule collision: two rules produce opposite effects
- Memory corruption: state values become inconsistent

The generator creates glitches, the classifier predicts impact,
and the resolver suggests repair strategies.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Glitch:
    glitch_id: str
    glitch_type: str
    severity: float
    affected_agents: list[str]
    description: str
    repair_strategy: str
    tick_created: int = 0
    resolved: bool = False

    def payload(self) -> dict[str, Any]:
        return {
            "glitch_id": self.glitch_id,
            "type": self.glitch_type,
            "severity": round(self.severity, 4),
            "affected": self.affected_agents,
            "description": self.description,
            "repair": self.repair_strategy,
            "resolved": self.resolved,
        }


GLITCH_TEMPLATES = {
    "identity_split": {
        "descriptions": [
            "Agent {agent} holds contradictory beliefs about {topic}",
            "Agent {agent} simultaneously acts as {role_a} and {role_b}",
            "Agent {agent} has conflicting position memories at {pos}",
        ],
        "repairs": ["force_consolidation", "belief_arbitration", "identity_reset"],
        "base_severity": 0.4,
    },
    "temporal_loop": {
        "descriptions": [
            "Agent {agent} repeats action sequence {action} indefinitely",
            "Tick {tick} state matches tick {tick2} — loop detected",
            "Action {action} at position {pos} creates infinite recursion",
        ],
        "repairs": ["break_loop", "inject_randomness", "state_override"],
        "base_severity": 0.6,
    },
    "rule_collision": {
        "descriptions": [
            "Rule A says {rule_a} but Rule B says {rule_b}",
            "Opposing directives from {source_a} and {source_b}",
            "Paradox: action {action} is both required and forbidden",
        ],
        "repairs": ["priority_override", "rule_merge", "disable_conflicting"],
        "base_severity": 0.5,
    },
    "memory_corruption": {
        "descriptions": [
            "Agent {agent} memory cell {cell} contains invalid value {value}",
            "State hash mismatch at position {pos}",
            "Agent {agent} believes it visited {pos} but no record exists",
        ],
        "repairs": ["memory_rollback", "consensus_restore", "isolation_quarantine"],
        "base_severity": 0.7,
    },
}


@dataclass
class GlitchPatternGenerator:
    """Generate, classify, and resolve synthetic glitches."""
    width: int = 16
    height: int = 16
    seed: int | None = None

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)
        self._glitches: list[Glitch] = []
        self._tick = 0

    def generate(self, count: int = 5) -> list[Glitch]:
        """Generate random glitches."""
        agents = [f"agent-{i}" for i in range(10)]
        topics = ["terrain", "alliance", "resources", "identity"]
        roles = ["scout", "guardian", "builder", "destroyer"]
        actions = ["move", "observe", "attack", "build", "rest"]

        new_glitches: list[Glitch] = []
        for _ in range(count):
            gtype = self._rng.choice(list(GLITCH_TEMPLATES.keys()))
            template = GLITCH_TEMPLATES[gtype]

            agent = self._rng.choice(agents)
            pos = (self._rng.randint(0, self.width - 1), self._rng.randint(0, self.height - 1))

            desc_template = self._rng.choice(template["descriptions"])
            description = desc_template.format(
                agent=agent, topic=self._rng.choice(topics),
                role_a=self._rng.choice(roles), role_b=self._rng.choice(roles),
                pos=list(pos), tick=self._tick, tick2=self._tick - 3,
                action=self._rng.choice(actions),
                rule_a="activate", rule_b="deactivate",
                source_a="protocol_A", source_b="protocol_B",
                cell=f"cell_{pos[0]}_{pos[1]}", value=round(self._rng.random(), 3),
            )

            severity = template["base_severity"] + self._rng.uniform(-0.1, 0.2)
            severity = max(0.1, min(1.0, severity))

            glitch = Glitch(
                glitch_id=hashlib.sha256(f"{gtype}:{agent}:{self._tick}".encode()).hexdigest()[:12],
                glitch_type=gtype,
                severity=severity,
                affected_agents=[agent],
                description=description,
                repair_strategy=self._rng.choice(template["repairs"]),
                tick_created=self._tick,
            )
            new_glitches.append(glitch)
            self._glitches.append(glitch)

        return new_glitches

    def classify_severity(self, glitch: Glitch) -> dict[str, Any]:
        """Classify a glitch's impact level."""
        if glitch.severity >= 0.8:
            level = "critical"
            impact = "System-wide instability; multiple agents affected"
        elif glitch.severity >= 0.6:
            level = "major"
            impact = "Significant disruption; localized damage"
        elif glitch.severity >= 0.4:
            level = "moderate"
            impact = "Noticeable but contained; quick repair possible"
        else:
            level = "minor"
            impact = "Cosmetic; minimal behavioral change"

        return {
            "level": level,
            "impact": impact,
            "repair_urgency": "immediate" if glitch.severity >= 0.7 else "scheduled",
        }

    def resolve_all(self) -> dict[str, Any]:
        """Resolve all unresolved glitches."""
        resolved = 0
        for glitch in self._glitches:
            if not glitch.resolved:
                glitch.resolved = True
                resolved += 1
        return {"resolved": resolved, "total": len(self._glitches)}

    def glitch_report(self) -> dict[str, Any]:
        type_dist = Counter(g.glitch_type for g in self._glitches)
        severity_dist = Counter()
        for g in self._glitches:
            classification = self.classify_severity(g)
            severity_dist[classification["level"]] += 1

        unresolved = [g for g in self._glitches if not g.resolved]
        return {
            "total_glitches": len(self._glitches),
            "unresolved": len(unresolved),
            "type_distribution": dict(type_dist),
            "severity_distribution": dict(severity_dist),
            "mean_severity": round(
                sum(g.severity for g in self._glitches) / max(1, len(self._glitches)), 4
            ),
            "most_severe": max(
                (g.payload() for g in self._glitches), key=lambda g: g["severity"], default=None
            ),
            "repair_strategies": dict(Counter(g.repair_strategy for g in self._glitches)),
        }


def demo() -> dict[str, Any]:
    gen = GlitchPatternGenerator(seed=42)
    new_glitches = gen.generate(count=10)
    report = gen.glitch_report()
    return {
        "new_glitches": [g.payload() for g in new_glitches],
        "report": report,
    }


def main() -> None:
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
