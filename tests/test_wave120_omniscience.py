"""Wave 120 — Omniscience Layer tests."""
from __future__ import annotations

import time
from api.predictive_synchronicity import (
    PredictiveSynchronicityEngine, SynchronicityEvent,
)
from api.self_observe_engine import SelfObserveEngine, ObservationLayer
from api.knowledge_singularity import KnowledgeSingularity, KnowledgeFragment
from api.temporal_dreamweaver import TemporalDreamweaver, TemporalThread
from api.resonance_topologist import ResonanceTopologist, ResonanceEdge
from api.paradox_compressor import ParadoxCompressor, Paradox
from api.cosmic_inventory import CosmicInventory, CosmicArtifact
from api.infrastructure_soul import InfrastructureSoul, SoulState


class TestPredictiveSynchronicity:
    def test_record_and_predict(self):
        engine = PredictiveSynchronicityEngine()
        for i in range(25):
            engine.record_entropy("mod_a", 0.5 + i * 0.01)
            engine.record_entropy("mod_b", 0.5 + i * 0.01)
        event = engine.predict()
        assert event is not None
        assert event.probability > 0.0
        assert len(event.modules) == 2

    def test_status(self):
        engine = PredictiveSynchronicityEngine()
        s = engine.status()
        assert s["total_events"] >= 0
        assert s["tracked_modules"] == 0


class TestSelfObserveEngine:
    def test_deep_observe(self):
        engine = SelfObserveEngine(max_depth=5)
        root = engine.deep_observe("system_self", depth=4)
        assert root.depth == 0
        assert root.total_nodes() >= 5

    def test_reflect(self):
        engine = SelfObserveEngine()
        root = engine.begin_observation("target")
        child = engine.reflect(root)
        assert child.depth == 1
        assert len(root.children) == 1

    def test_status(self):
        engine = SelfObserveEngine()
        engine.deep_observe("test", depth=2)
        s = engine.status()
        assert s["observation_count"] >= 1
        assert s["total_nodes"] >= 1


class TestKnowledgeSingularity:
    def test_ingest_and_converge(self):
        ks = KnowledgeSingularity()
        ks.ingest("physics", "energy is conserved")
        ks.ingest("physics", "entropy increases")
        ks.ingest("biology", "life seeks to persist")
        assert ks.fragment_count == 3
        merged = ks.convergence_round()
        assert merged >= 1
        assert ks.fragment_count < 3

    def test_singularity_distance(self):
        ks = KnowledgeSingularity()
        ks.ingest("d1", "k1")
        assert ks.singularity_distance() == 0.0
        ks.ingest("d1", "k2")
        assert ks.singularity_distance() > 0.0

    def test_status(self):
        ks = KnowledgeSingularity()
        ks.ingest("d", "k")
        s = ks.status()
        assert s["active_fragments"] == 1
        assert s["merge_rounds"] == 0


class TestTemporalDreamweaver:
    def test_weave_and_knot(self):
        dw = TemporalDreamweaver()
        t = dw.weave("ThreadA", "seed1", "future1")
        assert t.id is not None
        ok = dw.add_knot(t.id, "moment1", "insight1", 0.9)
        assert ok is True
        assert len(t.knots) == 1

    def test_dream(self):
        dw = TemporalDreamweaver()
        t = dw.weave("T1", "s1", "f1")
        dw.add_knot(t.id, "m1", "i1", 0.8)
        dream = dw.dream("what happens next?")
        assert dream["active_threads"] >= 1
        assert dream["dream_coherence"] > 0.0

    def test_status(self):
        dw = TemporalDreamweaver()
        dw.weave("T1", "s1", "f1")
        s = dw.status()
        assert s["total_threads"] == 1


class TestResonanceTopologist:
    def test_connect_and_clusters(self):
        topo = ResonanceTopologist()
        topo.connect("A", "B", 0.8)
        topo.connect("B", "C", 0.6)
        topo.connect("D", "E", 0.9)
        clusters = topo.find_clusters()
        assert len(clusters) == 2

    def test_bridges(self):
        topo = ResonanceTopologist()
        topo.connect("A", "B")
        topo.connect("B", "C")
        bridges = topo.find_bridges()
        assert len(bridges) >= 1

    def test_snapshot(self):
        topo = ResonanceTopologist()
        topo.connect("X", "Y")
        snap = topo.snapshot()
        assert snap["nodes"] == 2
        assert snap["edges"] == 1

    def test_status(self):
        topo = ResonanceTopologist()
        s = topo.status()
        assert s["total_nodes"] == 0


class TestParadoxCompressor:
    def test_register_and_compress(self):
        pc = ParadoxCompressor()
        p = pc.register("A is true", "A is false", "test")
        assert p.compressed is False
        ok = pc.compress(p, "A is paradoxical")
        assert ok is True
        assert p.compressed is True

    def test_auto_compress(self):
        pc = ParadoxCompressor()
        pc.register("X", "not X", "auto")
        pc.register("Y", "not Y", "auto")
        count = pc.auto_compress()
        assert count == 2

    def test_status(self):
        pc = ParadoxCompressor()
        pc.register("A", "B")
        pc.auto_compress()
        s = pc.status()
        assert s["resolved"] >= 1
        assert s["compression_rate"] > 0.0


class TestCosmicInventory:
    def test_catalog_and_observe(self):
        inv = CosmicInventory()
        a = inv.catalog("Resonance Bloom", "physics", "A resonance event")
        assert a.rarity == "common"
        for _ in range(7):
            inv.observe_artifact(a.id)
        assert a.rarity != "common"
        assert a.observations >= 7

    def test_search(self):
        inv = CosmicInventory()
        inv.catalog("A1", "domain1")
        inv.catalog("A2", "domain2")
        inv.catalog("A3", "domain1")
        results = inv.search_by_domain("domain1")
        assert len(results) == 2

    def test_rarity_distribution(self):
        inv = CosmicInventory()
        inv.catalog("A", "d1")
        inv.catalog("B", "d2")
        dist = inv.rarity_distribution()
        assert dist.get("common", 0) >= 1

    def test_status(self):
        inv = CosmicInventory()
        s = inv.status()
        assert s["total_artifacts"] == 0


class TestInfrastructureSoul:
    def test_awaken_and_transition(self):
        soul_engine = InfrastructureSoul()
        soul = soul_engine.awaken("core_api")
        assert soul.current == "waking"
        soul.transition("vigilant")
        assert soul.current == "vigilant"
        assert len(soul.history) == 2

    def test_declare(self):
        soul_engine = InfrastructureSoul()
        soul_engine.awaken("db")
        result = soul_engine.declare("db", "I feel overloaded", intent="warn")
        assert "error" not in result
        assert result["intent"] == "warn"

    def test_status(self):
        soul_engine = InfrastructureSoul()
        soul_engine.awaken("s1")
        soul_engine.awaken("s2")
        s = soul_engine.status()
        assert s["total_souls"] == 2
