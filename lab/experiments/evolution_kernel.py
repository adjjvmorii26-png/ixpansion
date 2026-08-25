#!/usr/bin/env python3
"""Evolution Kernel — meta-scheduler that observes and mutates the repo itself.

This module doesn't just participate in the system — it watches all
other modules and proposes evolutionary changes:
- Modules with high entropy get flagged for stabilization
- Modules with low usage get flagged for deprecation
- Modules with high cross-domain resonance get flagged for merging
- Fresh modules with high novelty get flagged for promotion

The kernel never executes mutations directly — it produces a
"differential" (a set of proposed changes) that must be approved
by a separate governance process.
"""
from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ModuleProfile:
    module_id: str
    name: str
    entropy: float = 0.5
    usage_frequency: float = 0.5
    cross_domain_resonance: float = 0.0
    novelty: float = 0.5
    age_ticks: int = 0
    last_mutation_tick: int = 0
    dependencies: list[str] = field(default_factory=list)
    dependents: list[str] = field(default_factory=list)

    @property
    def health_score(self) -> float:
        """Overall module health: balance of entropy, usage, and novelty."""
        return round(
            0.3 * (1.0 - self.entropy) +
            0.3 * self.usage_frequency +
            0.2 * self.cross_domain_resonance +
            0.2 * self.novelty,
            4,
        )

    @property
    def staleness(self) -> float:
        """How stale this module is (0=fresh, 1=very stale)."""
        return min(1.0, self.age_ticks / max(1, self.age_ticks + 20))

    def payload(self) -> dict[str, Any]:
        return {
            "module_id": self.module_id,
            "name": self.name,
            "entropy": round(self.entropy, 4),
            "usage": round(self.usage_frequency, 4),
            "resonance": round(self.cross_domain_resonance, 4),
            "novelty": round(self.novelty, 4),
            "health": self.health_score,
            "staleness": round(self.staleness, 4),
        }


@dataclass
class MutationProposal:
    proposal_id: str
    target_module: str
    mutation_type: str  # stabilize, deprecate, merge, promote, mutate
    reason: str
    priority: float
    affected_modules: list[str] = field(default_factory=list)
    approved: bool = False

    def payload(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "target": self.target_module,
            "type": self.mutation_type,
            "reason": self.reason,
            "priority": round(self.priority, 4),
            "affected": self.affected_modules,
            "approved": self.approved,
        }


@dataclass
class EvolutionKernel:
    """Meta-scheduler that observes and proposes mutations."""
    entropy_threshold: float = 0.7
    usage_threshold: float = 0.2
    resonance_threshold: float = 0.5
    novelty_threshold: float = 0.6
    seed: int | None = None

    def __post_init__(self) -> None:
        self._modules: dict[str, ModuleProfile] = {}
        self._proposals: list[MutationProposal] = []
        self._tick = 0
        self._differential_log: list[dict[str, Any]] = []

    def register_module(self, module_id: str, name: str, **kwargs: Any) -> ModuleProfile:
        profile = ModuleProfile(module_id=module_id, name=name, **kwargs)
        self._modules[module_id] = profile
        return profile

    def update_module(self, module_id: str, **kwargs: Any) -> None:
        if module_id in self._modules:
            for key, val in kwargs.items():
                if hasattr(self._modules[module_id], key):
                    setattr(self._modules[module_id], key, val)

    def tick(self) -> dict[str, Any]:
        self._tick += 1
        new_proposals: list[dict[str, Any]] = []

        for mid, profile in self._modules.items():
            profile.age_ticks += 1

            # High entropy → stabilize
            if profile.entropy > self.entropy_threshold:
                proposal = self._propose(mid, "stabilize",
                    f"Entropy {profile.entropy:.2f} exceeds threshold {self.entropy_threshold}",
                    priority=profile.entropy)
                new_proposals.append(proposal.payload())

            # Low usage → deprecate
            if (profile.usage_frequency < self.usage_threshold
                    and profile.age_ticks > 10
                    and not profile.dependents):
                proposal = self._propose(mid, "deprecate",
                    f"Usage {profile.usage_frequency:.2f} below threshold, no dependents",
                    priority=1.0 - profile.usage_frequency)
                new_proposals.append(proposal.payload())

            # High cross-domain resonance → merge candidate
            if profile.cross_domain_resonance > self.resonance_threshold:
                proposal = self._propose(mid, "merge_candidate",
                    f"Cross-domain resonance {profile.cross_domain_resonance:.2f} suggests merge opportunity",
                    priority=profile.cross_domain_resonance)
                new_proposals.append(proposal.payload())

            # High novelty + high usage → promote
            if (profile.novelty > self.novelty_threshold
                    and profile.usage_frequency > 0.5):
                proposal = self._propose(mid, "promote",
                    f"Novelty {profile.novelty:.2f} + usage {profile.usage_frequency:.2f} → promote",
                    priority=profile.novelty * profile.usage_frequency)
                new_proposals.append(proposal.payload())

        # Record differential
        self._differential_log.append({
            "tick": self._tick,
            "proposals": len(new_proposals),
            "modules_observed": len(self._modules),
        })

        return {"tick": self._tick, "new_proposals": len(new_proposals)}

    def _propose(self, target: str, mtype: str, reason: str,
                 priority: float) -> MutationProposal:
        pid = hashlib.sha256(
            f"{target}:{mtype}:{self._tick}".encode()
        ).hexdigest()[:12]
        proposal = MutationProposal(
            proposal_id=pid,
            target_module=target,
            mutation_type=mtype,
            reason=reason,
            priority=priority,
        )
        self._proposals.append(proposal)
        return proposal

    def approve_proposal(self, proposal_id: str) -> bool:
        for p in self._proposals:
            if p.proposal_id == proposal_id:
                p.approved = True
                return True
        return False

    def differential(self) -> dict[str, Any]:
        pending = [p for p in self._proposals if not p.approved]
        approved = [p for p in self._proposals if p.approved]
        type_counts = defaultdict(int)
        for p in pending:
            type_counts[p.mutation_type] += 1

        return {
            "tick": self._tick,
            "total_proposals": len(self._proposals),
            "pending": len(pending),
            "approved": len(approved),
            "pending_by_type": dict(type_counts),
            "top_priority": [
                p.payload() for p in sorted(pending, key=lambda x: -x.priority)[:5]
            ],
            "module_health": {
                mid: p.health_score for mid, p in self._modules.items()
            },
        }


def demo() -> dict[str, Any]:
    kernel = EvolutionKernel(seed=42)

    # Register modules from waves 72-76
    modules = [
        ("spectral_drift", 0.3, 0.7, 0.4, 0.8),
        ("temporal_resonance", 0.2, 0.6, 0.3, 0.7),
        ("cross_pollinator", 0.8, 0.5, 0.7, 0.6),
        ("memory_palace", 0.4, 0.3, 0.2, 0.5),
        ("neural_topology", 0.6, 0.8, 0.6, 0.7),
        ("consciousness_fingerprint", 0.1, 0.4, 0.1, 0.3),
        ("mood_synesthesia", 0.5, 0.9, 0.8, 0.9),
        ("glitch_generator", 0.9, 0.2, 0.1, 0.4),
    ]

    for name, entropy, usage, resonance, novelty in modules:
        kernel.register_module(name, name, entropy=entropy,
                               usage_frequency=usage,
                               cross_domain_resonance=resonance,
                               novelty=novelty)

    # Simulate 15 ticks of observation
    for _ in range(15):
        kernel.tick()
        # Some modules change over time
        kernel.update_module("cross_pollinator", entropy=0.6, usage_frequency=0.7)
        kernel.update_module("glitch_generator", usage_frequency=0.6, novelty=0.7)

    return kernel.differential()


def main() -> None:
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
