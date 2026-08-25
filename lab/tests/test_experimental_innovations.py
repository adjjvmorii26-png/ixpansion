"""Tests for experimental innovation modules."""
from __future__ import annotations

import pytest


# ── Spectral Drift Engine ──

class TestSpectralDrift:
    def test_import(self):
        from lab.experiments.spectral_drift import DriftEngine, SpectralState
        assert DriftEngine is not None
        assert SpectralState is not None

    def test_initialization_creates_trajectory(self):
        from lab.experiments.spectral_drift import DriftEngine
        engine = DriftEngine(seed=42)
        states = engine.initialize("test-agent", {"order": 0.8, "chaos": 0.2})
        assert len(states) == 1
        assert states[0].agent_id == "test-agent"
        assert states[0].tick == 0

    def test_drift_extends_trajectory(self):
        from lab.experiments.spectral_drift import DriftEngine
        engine = DriftEngine(seed=42)
        states = engine.initialize("test-agent")
        states = engine.drift("test-agent", states, ticks=10)
        assert len(states) == 11
        assert states[-1].tick == 10

    def test_drift_is_deterministic(self):
        from lab.experiments.spectral_drift import DriftEngine
        e1 = DriftEngine(seed=42)
        e2 = DriftEngine(seed=42)
        t1 = e1.drift("a", e1.initialize("a"), ticks=5)
        t2 = e2.drift("a", e2.initialize("a"), ticks=5)
        assert [s.fingerprint for s in t1] == [s.fingerprint for s in t2]

    def test_amplitudes_stay_in_bounds(self):
        from lab.experiments.spectral_drift import DriftEngine
        engine = DriftEngine(seed=42)
        states = engine.initialize("test-agent")
        states = engine.drift("test-agent", states, ticks=100)
        for state in states:
            for trait, amp in state.amplitudes.items():
                assert 0.0 <= amp <= 1.0, f"{trait}={amp} out of bounds at tick {state.tick}"

    def test_analyze_trajectory(self):
        from lab.experiments.spectral_drift import DriftEngine
        engine = DriftEngine(seed=42)
        states = engine.initialize("test-agent")
        states = engine.drift("test-agent", states, ticks=10)
        analysis = engine.analyze_trajectory(states)
        assert analysis["agent_id"] == "test-agent"
        assert analysis["ticks"] == 11
        assert "entropy_range" in analysis
        assert "converged" in analysis

    def test_analyze_empty_trajectory(self):
        from lab.experiments.spectral_drift import DriftEngine
        engine = DriftEngine(seed=42)
        analysis = engine.analyze_trajectory([])
        assert analysis["status"] == "empty"

    def test_entropy_is_non_negative(self):
        from lab.experiments.spectral_drift import DriftEngine
        engine = DriftEngine(seed=42)
        states = engine.initialize("test-agent")
        states = engine.drift("test-agent", states, ticks=20)
        for state in states:
            assert state.entropy >= 0.0


# ── Temporal Resonance Scanner ──

class TestTemporalResonance:
    def test_import(self):
        from lab.experiments.temporal_resonance import ResonanceScanner, Event
        assert ResonanceScanner is not None
        assert Event is not None

    def test_scan_empty(self):
        from lab.experiments.temporal_resonance import ResonanceScanner
        scanner = ResonanceScanner()
        result = scanner.scan([])
        assert result["motifs"] == []
        assert result["pulses"] == []

    def test_detects_periodic_pulses(self):
        from lab.experiments.temporal_resonance import ResonanceScanner, Event
        events = [Event(label="heartbeat", tick=i * 5, source="kernel") for i in range(20)]
        scanner = ResonanceScanner(min_pulse_count=3)
        result = scanner.scan(events)
        pulse_labels = [p["label"] for p in result["pulses"]]
        assert "heartbeat" in pulse_labels

    def test_detects_recurring_motifs(self):
        from lab.experiments.temporal_resonance import ResonanceScanner, Event
        events = []
        for cycle in range(10):
            events.append(Event(label="A", tick=cycle * 4, source="x"))
            events.append(Event(label="B", tick=cycle * 4 + 1, source="x"))
            events.append(Event(label="C", tick=cycle * 4 + 2, source="x"))
        scanner = ResonanceScanner(min_occurrences=2)
        result = scanner.scan(events)
        assert len(result["motifs"]) > 0
        sequences = [tuple(m["sequence"]) for m in result["motifs"]]
        assert ("A", "B", "C") in sequences

    def test_summary_has_correct_counts(self):
        from lab.experiments.temporal_resonance import ResonanceScanner, Event
        events = [Event(label="x", tick=i, source="test") for i in range(10)]
        scanner = ResonanceScanner()
        result = scanner.scan(events)
        assert result["summary"]["total_events"] == 10
        assert result["summary"]["unique_labels"] == 1

    def test_motif_strength_is_bounded(self):
        from lab.experiments.temporal_resonance import ResonanceScanner, Event
        events = []
        for i in range(15):
            events.append(Event(label="A", tick=i * 3, source="x"))
            events.append(Event(label="B", tick=i * 3 + 1, source="x"))
        scanner = ResonanceScanner(min_occurrences=2)
        result = scanner.scan(events)
        for motif in result["motifs"]:
            assert 0.0 <= motif["strength"] <= 1.0


# ── Paradox Breeding Chamber ──

class TestParadoxBreeding:
    def test_import(self):
        from lab.experiments.paradox_breeding import ParadoxChamber, ParadoxDNA
        assert ParadoxChamber is not None
        assert ParadoxDNA is not None

    def test_breed_produces_child(self):
        from lab.experiments.paradox_breeding import ParadoxChamber, ParadoxDNA
        chamber = ParadoxChamber(seed=42)
        a = ParadoxDNA(traits={"x": 0.8, "y": 0.2})
        b = ParadoxDNA(traits={"x": 0.3, "y": 0.9})
        child = chamber.breed(a, b)
        assert child.generation == 1
        assert len(child.traits) == 2
        assert child.parent_ids == (a.genome_id, b.genome_id)

    def test_breed_lineage_produces_sequence(self):
        from lab.experiments.paradox_breeding import ParadoxChamber, ParadoxDNA
        chamber = ParadoxChamber(seed=42)
        a = ParadoxDNA(traits={"x": 0.8, "y": 0.2})
        b = ParadoxDNA(traits={"x": 0.3, "y": 0.9})
        lineage = chamber.breed_lineage(a, b, generations=5)
        assert len(lineage) == 5
        assert lineage[-1]["generation"] == 5

    def test_child_traits_stay_in_bounds(self):
        from lab.experiments.paradox_breeding import ParadoxChamber, ParadoxDNA
        chamber = ParadoxChamber(seed=42)
        a = ParadoxDNA(traits={"x": 0.8, "y": 0.2})
        b = ParadoxDNA(traits={"x": 0.3, "y": 0.9})
        lineage = chamber.breed_lineage(a, b, generations=20)
        for entry in lineage:
            for trait, value in entry["traits"].items():
                assert 0.0 <= value <= 1.0, f"{trait}={value} out of bounds"

    def test_novelty_is_bounded(self):
        from lab.experiments.paradox_breeding import ParadoxChamber, ParadoxDNA
        chamber = ParadoxChamber(seed=42)
        a = ParadoxDNA(traits={"x": 0.8, "y": 0.2})
        b = ParadoxDNA(traits={"x": 0.3, "y": 0.9})
        lineage = chamber.breed_lineage(a, b, generations=5)
        for entry in lineage:
            assert 0.0 <= entry["novelty"] <= 1.0

    def test_tournament_selects_from_population(self):
        from lab.experiments.paradox_breeding import ParadoxChamber, ParadoxDNA
        chamber = ParadoxChamber(seed=42)
        pop = [
            ParadoxDNA(traits={"x": 1.0, "y": 0.0}),
            ParadoxDNA(traits={"x": 0.0, "y": 1.0}),
            ParadoxDNA(traits={"x": 0.5, "y": 0.5}),
        ]
        champion = chamber.tournament(pop, rounds=3)
        assert champion.genome_id in [p.genome_id for p in pop]


# ── Neural Topology Mapper ──

class TestNeuralTopology:
    def test_import(self):
        from lab.experiments.neural_topology import TopologyMapper
        assert TopologyMapper is not None

    def test_scan_produces_modules(self):
        from lab.experiments.neural_topology import TopologyMapper
        from pathlib import Path
        root = Path(__file__).resolve().parents[2]
        mapper = TopologyMapper(root=root)
        result = mapper.scan()
        assert "modules" in result
        assert "summary" in result
        assert result["summary"]["total_modules"] > 0

    def test_summary_fields(self):
        from lab.experiments.neural_topology import TopologyMapper
        from pathlib import Path
        root = Path(__file__).resolve().parents[2]
        mapper = TopologyMapper(root=root)
        result = mapper.scan()
        summary = result["summary"]
        assert "total_edges" in summary
        assert "components" in summary
        assert "hub_count" in summary
        assert "bridge_count" in summary

    def test_hub_modules_exist(self):
        from lab.experiments.neural_topology import TopologyMapper
        from pathlib import Path
        root = Path(__file__).resolve().parents[2]
        mapper = TopologyMapper(root=root)
        result = mapper.scan()
        # Should find at least some hubs in this large codebase
        assert result["summary"]["hub_count"] >= 0


# ── Cross-Pollinator ──

class TestCrossPollinator:
    def test_import(self):
        from lab.experiments.cross_pollinator import CrossPollinator, Signal
        assert CrossPollinator is not None
        assert Signal is not None

    def test_ingest_produces_pollinations(self):
        from lab.experiments.cross_pollinator import CrossPollinator, Signal
        pollinator = CrossPollinator(proximity_threshold=1.5, seed=42)
        signals = [
            Signal(source="A", label="x", features={"f1": 0.5, "f2": 0.3}, tick=0),
            Signal(source="B", label="y", features={"f1": 0.6, "f2": 0.4}, tick=0),
        ]
        result = pollinator.ingest(signals)
        assert len(result) > 0

    def test_same_source_no_pollination(self):
        from lab.experiments.cross_pollinator import CrossPollinator, Signal
        pollinator = CrossPollinator(proximity_threshold=0.1, seed=42)
        signals = [
            Signal(source="A", label="x", features={"f1": 0.5}, tick=0),
            Signal(source="A", label="y", features={"f1": 0.51}, tick=0),
        ]
        result = pollinator.ingest(signals)
        # Same source should not produce cross-pollinations
        for p in result:
            assert p.parent_a_source != p.parent_b_source

    def test_child_features_inherit_from_parents(self):
        from lab.experiments.cross_pollinator import CrossPollinator, Signal
        pollinator = CrossPollinator(proximity_threshold=2.0, seed=42)
        signals = [
            Signal(source="A", label="x", features={"f1": 0.8, "f2": 0.1}, tick=0),
            Signal(source="B", label="y", features={"f1": 0.2, "f2": 0.9}, tick=0),
        ]
        result = pollinator.ingest(signals)
        assert len(result) > 0
        child = result[0]
        # Child should have features from both parents
        assert "f1" in child.child_features
        assert "f2" in child.child_features

    def test_summary(self):
        from lab.experiments.cross_pollinator import CrossPollinator, Signal
        pollinator = CrossPollinator(proximity_threshold=1.5, seed=42)
        signals = [
            Signal(source="A", label="x", features={"f1": 0.5, "f2": 0.3}, tick=0),
            Signal(source="B", label="y", features={"f1": 0.6, "f2": 0.4}, tick=0),
            Signal(source="C", label="z", features={"f1": 0.55, "f2": 0.35}, tick=0),
        ]
        pollinator.ingest(signals)
        summary = pollinator.summary()
        assert summary["total_signals"] == 3
        assert summary["total_pollinations"] > 0


# ── Consciousness Fingerprint ──

class TestConsciousnessFingerprint:
    def test_import(self):
        from lab.experiments.consciousness_fingerprint import FingerprintEngine
        assert FingerprintEngine is not None

    def test_fingerprint_is_unique(self):
        from lab.experiments.consciousness_fingerprint import FingerprintEngine, SubsystemSample
        engine = FingerprintEngine(seed=42)
        samples = [SubsystemSample(source="test", metrics={"x": 0.5, "y": 0.3})]
        fp1 = engine.fingerprint(samples, run_id="run-1")
        fp2 = engine.fingerprint(samples, run_id="run-2")
        assert fp1.composite_hash != fp2.composite_hash

    def test_fingerprint_distance(self):
        from lab.experiments.consciousness_fingerprint import FingerprintEngine, SubsystemSample
        engine = FingerprintEngine(seed=42)
        s1 = [SubsystemSample(source="test", metrics={"x": 0.5, "y": 0.3})]
        s2 = [SubsystemSample(source="test", metrics={"x": 0.9, "y": 0.1})]
        fp1 = engine.fingerprint(s1)
        fp2 = engine.fingerprint(s2)
        assert fp1.distance(fp2) > 0

    def test_cosine_similarity_same_is_one(self):
        from lab.experiments.consciousness_fingerprint import FingerprintEngine, SubsystemSample
        engine = FingerprintEngine(seed=42)
        s = [SubsystemSample(source="test", metrics={"x": 0.5, "y": 0.3})]
        fp1 = engine.fingerprint(s, run_id="a")
        fp2 = engine.fingerprint(s, run_id="b")
        # Same metrics → cosine similarity should be 1.0
        assert abs(fp1.cosine_similarity(fp2) - 1.0) < 0.01

    def test_drift_analysis(self):
        from lab.experiments.consciousness_fingerprint import FingerprintEngine, SubsystemSample
        engine = FingerprintEngine(seed=42)
        sequence = []
        for i in range(5):
            s = [SubsystemSample(source="test", metrics={"x": 0.5 + i * 0.1, "y": 0.3 - i * 0.05})]
            sequence.append(engine.fingerprint(s, run_id=f"run-{i}"))
        drift = engine.drift_analysis(sequence)
        assert "trend" in drift
        assert "mean_similarity" in drift

    def test_birth_certificate(self):
        from lab.experiments.consciousness_fingerprint import FingerprintEngine, SubsystemSample
        engine = FingerprintEngine(seed=42)
        s = [SubsystemSample(source="test", metrics={"x": 0.5})]
        fp = engine.fingerprint(s, run_id="test-run")
        assert "test-run" in fp.birth_certificate


# ── Memory Palace ──

class TestMemoryPalace:
    def test_import(self):
        from lab.experiments.memory_palace import MemoryPalace
        assert MemoryPalace is not None

    def test_place_and_recall(self):
        from lab.experiments.memory_palace import MemoryPalace
        palace = MemoryPalace()
        palace.place("m1", "first memory")
        recalled = palace.recall("m1")
        assert recalled is not None
        assert recalled.content == "first memory"
        assert recalled.access_count == 1

    def test_proximity_scan(self):
        from lab.experiments.memory_palace import MemoryPalace
        palace = MemoryPalace()
        palace.place("m1", "near center", (50, 50))
        palace.place("m2", "far corner", (95, 95))
        near = palace.proximity_scan((50, 50), radius=20)
        assert len(near) == 1
        assert near[0].memory_id == "m1"

    def test_linking(self):
        from lab.experiments.memory_palace import MemoryPalace
        palace = MemoryPalace()
        palace.place("m1", "a")
        palace.place("m2", "b")
        palace.link("m1", "m2")
        connected = palace.connection_scan("m1")
        assert len(connected) == 1
        assert connected[0].memory_id == "m2"

    def test_tick_dissolves_dead_memories(self):
        from lab.experiments.memory_palace import MemoryPalace
        palace = MemoryPalace(dissolve_threshold=0.5, decay_rate=0.1)
        palace.place("m1", "ephemeral")
        palace.tick()  # salience drops
        palace.tick()
        palace.tick()
        palace.tick()
        palace.tick()  # salience = 1 - 5*0.1 = 0.5
        palace.tick()  # salience = 0.4 < 0.5 → dissolved
        assert palace.recall("m1") is None

    def test_landscape(self):
        from lab.experiments.memory_palace import MemoryPalace
        palace = MemoryPalace()
        palace.place("m1", "a", (10, 10))
        palace.place("m2", "b", (90, 90))
        palace.link("m1", "m2")
        landscape = palace.landscape()
        assert landscape["memory_count"] == 2
        assert landscape["total_links"] == 1


# ── Causal Causeway ──

class TestCausalCauseway:
    def test_import(self):
        from lab.experiments.causal_causeway import CausewayBuilder
        assert CausewayBuilder is not None

    def test_build_finds_concepts(self):
        from lab.experiments.causal_causeway import CausewayBuilder
        from pathlib import Path
        root = Path(__file__).resolve().parents[2]
        builder = CausewayBuilder(root=root)
        result = builder.build()
        assert result["summary"]["total_concepts"] > 0

    def test_build_finds_causeways(self):
        from lab.experiments.causal_causeway import CausewayBuilder
        from pathlib import Path
        root = Path(__file__).resolve().parents[2]
        builder = CausewayBuilder(root=root)
        result = builder.build()
        assert result["summary"]["total_causeways"] > 0

    def test_causeways_are_cross_project(self):
        from lab.experiments.causal_causeway import CausewayBuilder
        from pathlib import Path
        root = Path(__file__).resolve().parents[2]
        builder = CausewayBuilder(root=root)
        result = builder.build()
        for cw in result["causeways"]:
            assert cw["from_project"] != cw["to_project"], \
                f"Causeway {cw['causeway_id']} is not cross-project"

    def test_summary_has_project_pairs(self):
        from lab.experiments.causal_causeway import CausewayBuilder
        from pathlib import Path
        root = Path(__file__).resolve().parents[2]
        builder = CausewayBuilder(root=root)
        result = builder.build()
        assert len(result["summary"]["project_pairs"]) > 0
