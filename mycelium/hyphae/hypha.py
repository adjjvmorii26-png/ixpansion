"""Spores, hyphae, and the pulse loop of the living network."""
from __future__ import annotations

import copy
import random
from dataclasses import dataclass, field
from typing import Any

from mycelium.hyphae.consent import ConsentGate, GrowthProposal
from mycelium.nucleus.substrate import ResourceSite, Substrate


@dataclass(frozen=True)
class Spore:
    """A dormant, reproducible experiment seed."""

    spore_id: str
    genome: dict[str, float]
    viability: float = 0.7

    def __post_init__(self) -> None:
        if not 0 <= self.viability <= 1:
            raise ValueError("viability must be between zero and one")


@dataclass
class Hypha:
    """A living tip capable of perception, consent, and growth."""

    hypha_id: str
    genome: dict[str, float]
    position: tuple[float, float]
    energy: float
    viability: float
    trail: list[tuple[float, float]] = field(default_factory=list)
    memory: list[dict[str, Any]] = field(default_factory=list)


class HyphalNetwork:
    """Run consent-bounded pulses over a shared substrate."""

    def __init__(
        self,
        substrate: Substrate,
        *,
        seed: int | None = None,
        max_hyphae: int = 12,
        initial_energy: float = 1.0,
    ) -> None:
        if max_hyphae < 1:
            raise ValueError("max_hyphae must be positive")
        self.substrate = substrate
        self.rng = random.Random(seed)
        self.consent = ConsentGate()
        self.max_hyphae = max_hyphae
        self.initial_energy = initial_energy
        self.hyphae: dict[str, Hypha] = {}
        self.journal: list[dict[str, Any]] = []

    def plant(
        self,
        spore: Spore,
        position: tuple[float, float],
    ) -> str | None:
        """Germinate a spore if viability and carrying capacity permit."""
        if len(self.hyphae) >= self.max_hyphae or self.rng.random() > spore.viability:
            self.journal.append({
                "pulse": len(self.journal), "event": "dormant", "spore_id": spore.spore_id,
            })
            return None
        hypha_id = f"{spore.spore_id}-tip-{len(self.hyphae) + 1}"
        self.hyphae[hypha_id] = Hypha(
            hypha_id=hypha_id,
            genome=copy.deepcopy(spore.genome),
            position=position,
            energy=self.initial_energy,
            viability=spore.viability,
            trail=[position],
            memory=[{"event": "germinated"}],
        )
        self.journal.append({
            "pulse": len(self.journal), "event": "germinated",
            "hypha_id": hypha_id, "spore_id": spore.spore_id,
        })
        return hypha_id

    def _select_site(self, hypha: Hypha) -> ResourceSite | None:
        gradients = self.substrate.gradient(hypha.position)
        if not gradients:
            return None
        affinity = {
            site_id: score * (1.0 + hypha.genome.get(site_id[:4], 0.0))
            for site_id, score in gradients.items()
        }
        selected = max(sorted(affinity), key=lambda site_id: affinity[site_id])
        return self.substrate.sites[selected]

    def _move_toward(self, current: tuple[float, float], target: tuple[float, float]) -> tuple[float, float]:
        step = 0.18
        dx, dy = target[0] - current[0], target[1] - current[1]
        return round(current[0] + dx * step, 6), round(current[1] + dy * step, 6)

    def pulse(self) -> list[dict[str, Any]]:
        """Advance every living tip once under consent boundaries."""
        events: list[dict[str, Any]] = []
        for hypha_id in sorted(self.hyphae):
            hypha = self.hyphae[hypha_id]
            site = self._select_site(hypha)
            if site is None:
                continue

            compatibility = 1.0 + abs(hypha.genome.get("curiosity", 0.0))
            requested = min(0.45, max(0.05, site.nutrient * 0.12))
            offered = round(hypha.energy * hypha.viability * compatibility, 6)
            destination = self._move_toward(hypha.position, site.position)
            proposal = GrowthProposal(
                hypha_id=hypha_id,
                site_id=site.site_id,
                requested_nutrient=requested,
                offered_signal=offered,
                destination=destination,
            )

            decision = self.consent.decide(
                viability=hypha.viability,
                energy=hypha.energy,
                proposal=proposal,
            )
            granted = 0.0
            if decision.approved:
                granted = self.substrate.withdraw(site.site_id, requested)
                if granted <= 0:
                    decision = type(decision)(False, "substrate_reserved", 0.0)

            if decision.approved and granted > 0:
                hypha.position = destination
                hypha.trail.append(destination)
                hypha.energy += granted * 0.65 - 0.08
                self.substrate.deposit_signal(site.site_id, offered * 0.25)
                event_type = "exchange"
            else:
                hypha.energy -= 0.04
                event_type = "declined"

            event = {
                "event": event_type,
                "pulse_index": len(self.journal),
                "hypha_id": hypha_id,
                "site_id": site.site_id,
                "reason": decision.reason,
                "requested": round(requested, 6),
                "granted": round(granted, 6),
                "offered_signal": offered,
                "energy": round(max(0.0, hypha.energy), 6),
            }
            hypha.memory.append(event)
            self.journal.append(event)
            events.append(event)

            if hypha.energy > 2.2 and len(self.hyphae) < self.max_hyphae:
                child_genome = copy.deepcopy(hypha.genome)
                key = self.rng.choice(sorted(child_genome)) if child_genome else "curiosity"
                child_genome[key] = child_genome.get(key, 0.0) + self.rng.uniform(-0.08, 0.12)
                child = Hypha(
                    hypha_id=f"{hypha_id}-branch-{len(self.journal)}",
                    genome=child_genome,
                    position=self._move_toward(hypha.position, site.position),
                    energy=0.55,
                    viability=max(0.3, min(0.95, hypha.viability + self.rng.uniform(-0.03, 0.03))),
                    trail=[hypha.position],
                )
                self.hyphae[child.hypha_id] = child
                branch_event = {
                    "event": "branched", "pulse_index": len(self.journal),
                    "parent_id": hypha_id, "child_id": child.hypha_id,
                }
                self.journal.append(branch_event)
                events.append(branch_event)
                hypha.energy *= 0.62
        return events

    @property
    def stats(self) -> dict[str, Any]:
        exchanges = sum(item.get("event") == "exchange" for item in self.journal)
        declines = sum(item.get("event") == "declined" for item in self.journal)
        return {
            "living_tips": len(self.hyphae),
            "journal_events": len(self.journal),
            "exchanges": exchanges,
            "declines": declines,
            "substrate_nutrient": round(self.substrate.total_nutrient, 6),
        }
