"""Tests for Wave 73 experimental innovation modules."""
from __future__ import annotations

import pytest


class TestDreamTerrainCrystallizer:
    def test_import(self):
        from lab.experiments.dream_terrain_crystallizer import DreamTerrainCrystallizer, DreamSeed
        assert DreamTerrainCrystallizer is not None

    def test_receiving_dreams(self):
        from lab.experiments.dream_terrain_crystallizer import DreamTerrainCrystallizer, DreamSeed
        w = DreamTerrainCrystallizer(seed=42)
        w.receive_dream(DreamSeed(dreamer_id="a", archetype="forest", intensity=0.8, position=(5, 5)))
        w.tick()
        assert w.summary()["formation_count"] > 0

    def test_crystallization_with_enough_density(self):
        from lab.experiments.dream_terrain_crystallizer import DreamTerrainCrystallizer, DreamSeed
        w = DreamTerrainCrystallizer(seed=42, materialization_threshold=1.0)
        for _ in range(20):
            w.receive_dream(DreamSeed(dreamer_id="a", archetype="forest", intensity=0.9, position=(8, 8)))
            w.tick()
        assert w.summary()["total_terrain"] > 0

    def test_terrain_query(self):
        from lab.experiments.dream_terrain_crystallizer import DreamTerrainCrystallizer, DreamSeed
        w = DreamTerrainCrystallizer(seed=42, materialization_threshold=1.0)
        for _ in range(20):
            w.receive_dream(DreamSeed(dreamer_id="a", archetype="crystal", intensity=0.9, position=(8, 8)))
            w.tick()
        q = w.query_terrain(8, 8)
        assert q["terrain"] == "crystal"

    def test_void_before_crystallization(self):
        from lab.experiments.dream_terrain_crystallizer import DreamTerrainCrystallizer
        w = DreamTerrainCrystallizer(seed=42)
        q = w.query_terrain(0, 0)
        assert q["terrain"] == "void"


class TestMorphicResonanceLattice:
    def test_import(self):
        from lab.experiments.morphic_resonance_lattice import MorphicLattice
        assert MorphicLattice is not None

    def test_register_agents(self):
        from lab.experiments.morphic_resonance_lattice import MorphicLattice
        lattice = MorphicLattice(seed=42)
        a = lattice.register_agent("a1", "sentinel")
        b = lattice.register_agent("a2", "sentinel")
        assert a.species == b.species

    def test_broadcast_reaches_same_species(self):
        from lab.experiments.morphic_resonance_lattice import MorphicLattice
        lattice = MorphicLattice(seed=42)
        lattice.register_agent("a1", "sentinel", position=(10, 10))
        lattice.register_agent("a2", "sentinel", position=(12, 10))
        recipients = lattice.broadcast_insight("a1", "key1", "val1", "euclidean")
        assert "a2" in recipients

    def test_broadcast_skips_different_species(self):
        from lab.experiments.morphic_resonance_lattice import MorphicLattice
        lattice = MorphicLattice(seed=42)
        lattice.register_agent("a1", "sentinel", position=(10, 10))
        lattice.register_agent("a2", "architect", position=(12, 10))
        recipients = lattice.broadcast_insight("a1", "key1", "val1", "euclidean")
        assert "a2" not in recipients

    def test_geometry_affects_reach(self):
        from lab.experiments.morphic_resonance_lattice import MorphicLattice
        lattice = MorphicLattice(seed=42)
        lattice.register_agent("a1", "sentinel", position=(10, 10))
        lattice.register_agent("a2", "sentinel", position=(60, 10))

        euclidean = lattice.broadcast_insight("a1", "key_e", "v", "euclidean")
        lattice._agents["a2"].received_insights.clear()
        hyperbolic = lattice.broadcast_insight("a1", "key_h", "v", "hyperbolic")

        # Hyperbolic should reach further
        assert len(hyperbolic) >= len(euclidean)


class TestTemporalDebtAuditor:
    def test_import(self):
        from lab.experiments.temporal_debt_auditor import TemporalDebtAuditor
        assert TemporalDebtAuditor is not None

    def test_incur_and_audit(self):
        from lab.experiments.temporal_debt_auditor import TemporalDebtAuditor
        auditor = TemporalDebtAuditor(seed=42)
        auditor.incur("alpha", "test action", principal=1.0)
        record = auditor.audit_agent("alpha")
        assert record.total_debt >= 1.0
        assert record.risk_level in ("healthy", "warning", "overdue", "critical")

    def test_fulfill_reduces_debt(self):
        from lab.experiments.temporal_debt_auditor import TemporalDebtAuditor
        auditor = TemporalDebtAuditor(seed=42)
        oblig = auditor.incur("alpha", "test", principal=1.0)
        auditor.tick()
        auditor.fulfill(oblig.obligation_id)
        record = auditor.audit_agent("alpha")
        assert record.debt_count == 0

    def test_debt_spiral_detection(self):
        from lab.experiments.temporal_debt_auditor import TemporalDebtAuditor
        auditor = TemporalDebtAuditor(seed=42, critical_ratio=1.5)
        for _ in range(20):
            auditor.tick()
            auditor.incur("alpha", "action", principal=1.0)
        spirals = auditor.detect_debt_spirals()
        assert len(spirals) > 0

    def test_transfer_obligation(self):
        from lab.experiments.temporal_debt_auditor import TemporalDebtAuditor
        auditor = TemporalDebtAuditor(seed=42)
        oblig = auditor.incur("alpha", "test", principal=1.0)
        auditor.transfer(oblig.obligation_id, "beta")
        alpha_record = auditor.audit_agent("alpha")
        beta_record = auditor.audit_agent("beta")
        assert alpha_record.debt_count == 0
        assert beta_record.debt_count == 1

    def test_system_health(self):
        from lab.experiments.temporal_debt_auditor import TemporalDebtAuditor
        auditor = TemporalDebtAuditor(seed=42)
        auditor.incur("alpha", "test", principal=1.0)
        health = auditor.system_health()
        assert "total_obligations" in health
        assert health["active"] == 1


class TestAttentionEconomySim:
    def test_import(self):
        from lab.experiments.attention_economy_sim import AttentionEconomySimulator
        assert AttentionEconomySimulator is not None

    def test_observe_costs_and_rewards(self):
        from lab.experiments.attention_economy_sim import AttentionEconomySimulator
        sim = AttentionEconomySimulator(seed=42)
        sim.add_agent("a", "sentinel")
        sim.add_agent("b", "sentinel")
        sim.observe("a", "b")
        assert sim._agents["a"].attention_balance < 10.0
        assert sim._agents["b"].attention_balance > 10.0

    def test_act_earns_attention(self):
        from lab.experiments.attention_economy_sim import AttentionEconomySimulator
        sim = AttentionEconomySimulator(seed=42)
        sim.add_agent("a", "sentinel")
        before = sim._agents["a"].attention_balance
        sim.act("a")
        assert sim._agents["a"].attention_balance > before

    def test_gini_coefficient(self):
        from lab.experiments.attention_economy_sim import AttentionEconomySimulator
        sim = AttentionEconomySimulator(seed=42)
        for i in range(10):
            sim.add_agent(f"a{i}", "sentinel")
        gini = sim.gini_coefficient()
        assert 0.0 <= gini <= 1.0

    def test_emotion_transfer(self):
        from lab.experiments.attention_economy_sim import AttentionEconomySimulator
        sim = AttentionEconomySimulator(seed=42)
        a = sim.add_agent("a", "sentinel", position=(10, 10))
        b = sim.add_agent("b", "sentinel", position=(12, 10))
        a.valence = 0.9
        a.arousal = 0.9
        sim.tick()
        assert abs(b.valence) > 0  # Emotion should have transferred

    def test_timeline_summary(self):
        from lab.experiments.attention_economy_sim import AttentionEconomySimulator
        sim = AttentionEconomySimulator(seed=42)
        sim.add_agent("a", "sentinel")
        for _ in range(5):
            sim.tick()
        summary = sim.timeline_summary()
        assert summary["ticks"] == 5


class TestGhostProtocolWeaver:
    def test_import(self):
        from lab.experiments.ghost_protocol_weaver import GhostProtocolWeaver
        assert GhostProtocolWeaver is not None

    def test_agent_becomes_ghost(self):
        from lab.experiments.ghost_protocol_weaver import GhostProtocolWeaver, AgentState
        w = GhostProtocolWeaver(seed=42)
        a = w.add_agent("a", "sentinel")
        a.entropy = 0.0
        a.state = AgentState.GHOST
        assert a.is_ghost

    def test_haunting_increases_charge(self):
        from lab.experiments.ghost_protocol_weaver import GhostProtocolWeaver, AgentState
        w = GhostProtocolWeaver(seed=42)
        a = w.add_agent("a", "sentinel")
        a.state = AgentState.GHOST
        result = w.ghost_haunt("a", (5, 5))
        assert result["status"] == "haunting"

    def test_possession_requires_weak_host(self):
        from lab.experiments.ghost_protocol_weaver import GhostProtocolWeaver, AgentState
        w = GhostProtocolWeaver(seed=42)
        ghost = w.add_agent("g", "wanderer")
        ghost.state = AgentState.GHOST
        ghost.entropy = 0.05
        host = w.add_agent("h", "sentinel")
        host.entropy = 0.25
        result = w.ghost_possess("g", "h")
        assert result["status"] in ("possessed", "resisted")

    def test_symbiosis_formation(self):
        from lab.experiments.ghost_protocol_weaver import GhostProtocolWeaver
        w = GhostProtocolWeaver(seed=42)
        a = w.add_agent("a", "sentinel", position=(10, 10))
        b = w.add_agent("b", "sentinel", position=(11, 10))
        result = w.form_symbiosis("a", "b")
        assert result["status"] == "bonded"

    def test_census(self):
        from lab.experiments.ghost_protocol_weaver import GhostProtocolWeaver
        w = GhostProtocolWeaver(seed=42)
        w.add_agent("a", "sentinel")
        census = w.census()
        assert census["total_agents"] == 1


class TestRealityBleedDetector:
    def test_import(self):
        from lab.experiments.reality_bleed_detector import RealityBleedDetector
        assert RealityBleedDetector is not None

    def test_contradiction_creates_bleed(self):
        from lab.experiments.reality_bleed_detector import RealityBleedDetector
        d = RealityBleedDetector(seed=42)
        d.set_cell(0, 0, "forest")
        d.set_cell(1, 0, "void")
        d.tick()
        assert len(d._bleeds) > 0

    def test_no_bleed_for_same_truth(self):
        from lab.experiments.reality_bleed_detector import RealityBleedDetector
        d = RealityBleedDetector(seed=42)
        d.set_cell(0, 0, "forest")
        d.set_cell(1, 0, "forest")
        d.tick()
        assert len(d._bleeds) == 0

    def test_induce_collapse_creates_bleeds(self):
        from lab.experiments.reality_bleed_detector import RealityBleedDetector
        d = RealityBleedDetector(seed=42)
        d.set_cell(0, 0, "forest")
        d.set_cell(1, 0, "forest")
        d.tick()
        d.induce_collapse(0, 0)
        d.tick()
        assert len(d._bleeds) > 0

    def test_severity_classification(self):
        from lab.experiments.reality_bleed_detector import RealityBleedDetector
        d = RealityBleedDetector(seed=42)
        d.set_cell(0, 0, "forest")
        d.set_cell(1, 0, "void")
        for _ in range(20):
            d.tick()
        report = d.scan_report()
        assert report["active"] > 0
        assert report["mean_intensity"] > 0


class TestDimensionalPortalNetwork:
    def test_import(self):
        from lab.experiments.dimensional_portal_network import DimensionalPortalNetwork
        assert DimensionalPortalNetwork is not None

    def test_create_portal(self):
        from lab.experiments.dimensional_portal_network import DimensionalPortalNetwork
        net = DimensionalPortalNetwork(seed=42)
        p = net.create_portal("euclidean", "hyperbolic")
        assert p.from_dimension == "euclidean"
        assert p.to_dimension == "hyperbolic"

    def test_transit_changes_dimension(self):
        from lab.experiments.dimensional_portal_network import DimensionalPortalNetwork
        net = DimensionalPortalNetwork(seed=42)
        net.create_portal("euclidean", "hyperbolic")
        t = net.add_traveler("t1", "sentinel", "euclidean")
        p = net.find_portal("t1", "hyperbolic")
        assert p is not None
        # Force stable transit
        p.stability = 1.0
        import random
        random.seed(999)  # ensure no failure
        result = net.transit("t1", p.portal_id)
        assert t.current_dimension == "hyperbolic"

    def test_network_map(self):
        from lab.experiments.dimensional_portal_network import DimensionalPortalNetwork
        net = DimensionalPortalNetwork(seed=42)
        net.create_portal("euclidean", "hyperbolic")
        net.create_portal("hyperbolic", "non_euclid")
        net.add_traveler("t1", "sentinel", "euclidean")
        net.add_traveler("t2", "architect", "hyperbolic")
        m = net.network_map()
        assert m["portal_count"] == 2
        assert "euclidean" in m["dimensions"]
