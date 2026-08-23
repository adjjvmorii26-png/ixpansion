from mycelium.hyphae.consent import ConsentGate, GrowthProposal
from mycelium.hyphae.hypha import HyphalNetwork, Spore
from mycelium.nucleus.substrate import ResourceSite, Substrate


def build_network(seed=42, steps=4):
    substrate = Substrate()
    positions = [(0, 0), (3, 0), (0, 3), (-2, 2), (2, -2)]
    for index, position in enumerate(positions):
        substrate.add_site(ResourceSite(f"site-{index}", position, nutrient=9 + index))
    network = HyphalNetwork(substrate, seed=seed)
    network.plant(Spore("root", {"curiosity": 0.3}, viability=0.85), (0, 0))
    for _ in range(steps):
        network.pulse()
    return network


class TestConsentAndHyphae:
    def test_consent_requires_viability_signal_and_energy(self):
        gate = ConsentGate()
        proposal = GrowthProposal("h", "s", 1.0, 1.0, (0, 0))
        assert gate.decide(viability=.1, energy=1, proposal=proposal).approved is False
        assert gate.decide(viability=.8, energy=0, proposal=proposal).approved is False
        weak = GrowthProposal("h", "s", 1.0, .01, (0, 0))
        assert gate.decide(viability=.8, energy=1, proposal=weak).approved is False
        assert gate.decide(viability=.8, energy=1, proposal=proposal).approved is True

    def test_equal_seeds_have_identical_lived_history(self):
        first, second = build_network(seed=19), build_network(seed=19)
        assert first.journal == second.journal
        assert first.stats == second.stats
        assert [hypha.trail for hypha in first.hyphae.values()] == [
            hypha.trail for hypha in second.hyphae.values()
        ]

    def test_pulse_creates_exchange_or_decline_events(self):
        network = build_network(seed=42, steps=5)
        kinds = [item.get("event") for item in network.journal]
        assert "exchange" in kinds or "declined" in kinds
        assert network.stats["journal_events"] >= 5
        assert all(hypha.energy >= 0 for hypha in network.hyphae.values())

    def test_carrying_capacity_blocks_new_growth(self):
        substrate = Substrate()
        substrate.add_site(ResourceSite("site", (0, 0), nutrient=20))
        network = HyphalNetwork(substrate, max_hyphae=1, seed=7)
        first = network.plant(Spore("one", {}, viability=1), (0, 0))
        second = network.plant(Spore("two", {}, viability=1), (0, 0))
        assert first is not None
        assert second is None
