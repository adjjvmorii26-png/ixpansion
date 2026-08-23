"""Compile lived network events into reproducible dream experiments."""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from typing import Any

from mycelium.hyphae.hypha import HyphalNetwork, Spore


@dataclass(frozen=True)
class DreamExperiment:
    """A executable hypothesis distilled from a living pulse history."""

    dream_id: str
    hypothesis: str
    genome: dict[str, float]
    entropy_budget: float
    recommended_steps: int
    confidence: float
    evidence_hash: str

    def payload(self) -> dict[str, Any]:
        return asdict(self)

    def to_spore(self) -> Spore:
        return Spore(
            spore_id=f"dream-{self.dream_id[:12]}",
            genome=dict(self.genome),
            viability=max(0.35, min(0.95, self.confidence)),
        )


class DreamCompiler:
    """Turn consent exchanges, refusals, and branches into a testable dream."""

    def compile(self, network: HyphalNetwork) -> DreamExperiment | None:
        events = [event for event in network.journal if event.get("event") in {
            "exchange", "declined", "branched",
        }]
        if not events:
            return None

        exchanges = [item for item in events if item.get("event") == "exchange"]
        declined = [item for item in events if item.get("event") == "declined"]
        branched = [item for item in events if item.get("event") == "branched"]
        total = len(events)
        acceptance_rate = len(exchanges) / total
        refusal_pressure = len(declined) / total
        branch_rate = len(branched) / total

        site_scores: dict[str, float] = {}
        genome_sum: dict[str, float] = {}
        genome_count: dict[str, int] = {}
        granted_total = 0.0
        offered_total = 0.0
        for hypha in network.hyphae.values():
            for key, value in hypha.genome.items():
                genome_sum[key] = genome_sum.get(key, 0.0) + value
                genome_count[key] = genome_count.get(key, 0) + 1
            for memory in hypha.memory:
                if memory.get("event") != "exchange":
                    continue
                site_id = memory["site_id"]
                weight = float(memory.get("granted", 0.0)) + 0.01
                site_scores[site_id] = site_scores.get(site_id, 0.0) + weight
                granted_total += float(memory.get("granted", 0.0))
                offered_total += float(memory.get("offered_signal", 0.0))

        dominant_site = (
            min(sorted(site_scores), key=lambda site_id: (-site_scores[site_id], site_id))
            if site_scores else "unknown"
        )
        genome = {
            key: round(value / genome_count[key], 6)
            for key, value in sorted(genome_sum.items())
        }
        # A dream amplifies the least-satisfied signal rather than copying success.
        target_key = min(sorted(genome), key=lambda key: (genome[key], key)) if genome else "curiosity"
        dream_genome = dict(genome)
        dream_genome[target_key] = round(dream_genome.get(target_key, 0.0) + 0.18, 6)
        dream_genome.setdefault("curiosity", 0.25)

        efficiency = granted_total / offered_total if offered_total else 0.0
        confidence = max(0.05, min(0.95, 0.45 + acceptance_rate * 0.4 + efficiency * 0.2))
        entropy_budget = round(0.08 + refusal_pressure * 0.3 + branch_rate * 0.12, 6)
        recommended_steps = max(3, min(12, 4 + int(round(refusal_pressure * 8))))
        hypothesis = (
            f"Increase {target_key} sensitivity near {dominant_site}; "
            f"refusal pressure {refusal_pressure:.2f} may reveal a viable boundary."
        )

        evidence_inputs = {
            "confidence": confidence,
            "dominant_site": dominant_site,
            "dream_genome": dream_genome,
            "entropy_budget": entropy_budget,
            "events": events,
            "recommended_steps": recommended_steps,
            "seed_state": network.stats,
        }
        evidence_hash = hashlib.sha256(
            json.dumps(evidence_inputs, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        dream_id = hashlib.sha256((hypothesis + evidence_hash).encode("utf-8")).hexdigest()

        return DreamExperiment(
            dream_id=dream_id,
            hypothesis=hypothesis,
            genome=dream_genome,
            entropy_budget=entropy_budget,
            recommended_steps=recommended_steps,
            confidence=round(confidence, 6),
            evidence_hash=evidence_hash,
        )


def build_demo_network(seed: int, steps: int, site_count: int = 5) -> HyphalNetwork:
    """Create the stable ritual substrate used by CLI and nightly experiments."""
    import random

    from mycelium.nucleus.substrate import ResourceSite, Substrate

    if steps < 0:
        raise ValueError("steps cannot be negative")
    if not 1 <= site_count <= 24:
        raise ValueError("site_count must be between 1 and 24")

    rng = random.Random(seed)
    substrate = Substrate()
    for index in range(site_count):
        angle = (math.tau / site_count) * index
        radius = 1.5 + (index % 3) * 0.65
        position = (round(math.cos(angle) * radius, 6), round(math.sin(angle) * radius, 6))
        nutrient = round(7.0 + rng.uniform(0.0, 5.0), 6)
        substrate.add_site(ResourceSite(f"site-{index:02d}", position, nutrient=nutrient))

    network = HyphalNetwork(substrate, seed=seed)
    network.plant(
        Spore(
            spore_id="aleph-spore",
            genome={"curiosity": 0.32, "patience": 0.48},
            viability=0.82,
        ),
        position=(0.0, 0.0),
    )
    for _ in range(steps):
        network.pulse()
    return network
