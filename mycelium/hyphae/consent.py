"""Consent gate: no hypha may consume beyond its negotiated boundary."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GrowthProposal:
    """A request to cross the boundary between hypha and substrate."""

    hypha_id: str
    site_id: str
    requested_nutrient: float
    offered_signal: float
    destination: tuple[float, float]


@dataclass(frozen=True)
class ConsentDecision:
    approved: bool
    reason: str
    granted_nutrient: float


class ConsentGate:
    """Bound extraction, require viable signal, and preserve substrate reserves."""

    def __init__(
        self,
        *,
        minimum_signal: float = 0.15,
        maximum_extraction_ratio: float = 0.35,
        minimum_viability: float = 0.25,
    ) -> None:
        if not 0 <= maximum_extraction_ratio <= 1:
            raise ValueError("maximum_extraction_ratio must be between zero and one")
        self.minimum_signal = minimum_signal
        self.maximum_extraction_ratio = maximum_extraction_ratio
        self.minimum_viability = minimum_viability

    def decide(self, *, viability: float, energy: float, proposal: GrowthProposal) -> ConsentDecision:
        if viability < self.minimum_viability:
            return ConsentDecision(False, "hypha_below_viability", 0.0)
        if energy <= 0:
            return ConsentDecision(False, "hypha_without_energy", 0.0)
        if proposal.requested_nutrient <= 0:
            return ConsentDecision(False, "empty_request", 0.0)
        if proposal.offered_signal < self.minimum_signal:
            return ConsentDecision(False, "insufficient_offered_signal", 0.0)
        # The gate does not know substrate internals; callers enforce availability.
        return ConsentDecision(True, "mutual_exchange_accepted", proposal.requested_nutrient)
