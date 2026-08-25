"""Tests for Wave 74 experimental innovation modules."""
from __future__ import annotations

import pytest


class TestMoodSynesthesia:
    def test_import(self):
        from lab.experiments.mood_synesthesia import SynesthesiaEngine, MoodVector
        assert SynesthesiaEngine is not None

    def test_translate_visual(self):
        from lab.experiments.mood_synesthesia import SynesthesiaEngine, MoodVector
        engine = SynesthesiaEngine(seed=42)
        mood = MoodVector(valence=0.8, arousal=0.3, label="serenity")
        expr = engine.mood_to_channel(mood, "visual")
        assert expr.channel == "visual"
        assert "transparency" in expr.values
        assert "luminance" in expr.values

    def test_synthesize_full(self):
        from lab.experiments.mood_synesthesia import SynesthesiaEngine, MoodVector
        engine = SynesthesiaEngine(seed=42)
        mood = MoodVector(valence=-0.5, arousal=0.9, label="panic")
        result = engine.synthesize_full(mood)
        assert len(result["channels"]) == 4
        assert result["mood"]["label"] == "panic"

    def test_invalid_channel(self):
        from lab.experiments.mood_synesthesia import SynesthesiaEngine, MoodVector
        engine = SynesthesiaEngine(seed=42)
        with pytest.raises(ValueError):
            engine.mood_to_channel(MoodVector(0, 0), "nonexistent")

    def test_all_values_bounded(self):
        from lab.experiments.mood_synesthesia import SynesthesiaEngine, MoodVector
        engine = SynesthesiaEngine(seed=42)
        for v in [-1.0, -0.5, 0.0, 0.5, 1.0]:
            for a in [0.0, 0.3, 0.7, 1.0]:
                result = engine.synthesize_full(MoodVector(valence=v, arousal=a))
                for ch, expr in result["channels"].items():
                    for dim, val in expr["values"].items():
                        assert 0.0 <= val <= 1.0, f"{ch}.{dim}={val} out of bounds"


class TestNegativeSpaceCartographer:
    def test_import(self):
        from lab.experiments.negative_space_cartographer import NegativeSpaceCartographer
        assert NegativeSpaceCartographer is not None

    def test_empty_world_all_absent(self):
        from lab.experiments.negative_space_cartographer import NegativeSpaceCartographer, PresenceMap
        cart = NegativeSpaceCartographer(width=4, height=4)
        world = PresenceMap(width=4, height=4)
        result = cart.scan(world)
        assert result["total_absences"] == 16
        assert result["presence_ratio"] == 0.0

    def test_full_world_no_absences(self):
        from lab.experiments.negative_space_cartographer import NegativeSpaceCartographer, PresenceMap
        cart = NegativeSpaceCartographer(width=4, height=4)
        world = PresenceMap(width=4, height=4)
        for x in range(4):
            for y in range(4):
                world.set_cell(x, y, "filled")
        result = cart.scan(world)
        assert result["total_absences"] == 0

    def test_blind_spot_detection(self):
        from lab.experiments.negative_space_cartographer import NegativeSpaceCartographer, PresenceMap
        cart = NegativeSpaceCartographer(width=6, height=6)
        world = PresenceMap(width=6, height=6)
        # Fill everything except center
        for x in range(6):
            for y in range(6):
                if (x, y) != (3, 3):
                    world.set_cell(x, y, "content")
        result = cart.scan(world)
        categories = [a["category"] for a in result["notable_absences"]]
        assert "blind_spot" in categories

    def test_categories_are_valid(self):
        from lab.experiments.negative_space_cartographer import NegativeSpaceCartographer, PresenceMap
        cart = NegativeSpaceCartographer(width=8, height=8)
        world = PresenceMap(width=8, height=8)
        for x in range(8):
            for y in range(8):
                if (x + y) % 3 != 0:
                    world.set_cell(x, y, "type_a")
        result = cart.scan(world)
        valid = {"blind_spot", "deep_frontier", "compressed_gap", "transition_zone", "open_void"}
        for cat in result["categories"]:
            assert cat in valid


class TestPulseHarmonicsAnalyzer:
    def test_import(self):
        from lab.experiments.pulse_harmonics_analyzer import PulseHarmonicsAnalyzer
        assert PulseHarmonicsAnalyzer is not None

    def test_record_and_analyze(self):
        from lab.experiments.pulse_harmonics_analyzer import PulseHarmonicsAnalyzer
        import math
        analyzer = PulseHarmonicsAnalyzer()
        for i in range(30):
            analyzer.record("test", 0.5 + 0.3 * math.sin(2 * math.pi * i / 5))
        result = analyzer.analyze("test")
        assert result["samples"] == 30
        assert result["period"] > 0

    def test_insufficient_data(self):
        from lab.experiments.pulse_harmonics_analyzer import PulseHarmonicsAnalyzer
        analyzer = PulseHarmonicsAnalyzer()
        analyzer.record("test", 0.5)
        result = analyzer.analyze("test")
        assert result["status"] == "insufficient_data"

    def test_cross_source_phase(self):
        from lab.experiments.pulse_harmonics_analyzer import PulseHarmonicsAnalyzer
        import math
        analyzer = PulseHarmonicsAnalyzer()
        for i in range(30):
            analyzer.record("a", math.sin(2 * math.pi * i / 4))
            analyzer.record("b", math.cos(2 * math.pi * i / 4))
        result = analyzer.cross_source_phase()
        assert "a<->b" in result

    def test_harmonics_detected(self):
        from lab.experiments.pulse_harmonics_analyzer import PulseHarmonicsAnalyzer
        import math
        analyzer = PulseHarmonicsAnalyzer()
        for i in range(60):
            analyzer.record("src", 0.5 + 0.4 * math.sin(2 * math.pi * i / 6) + 0.2 * math.sin(2 * math.pi * i / 3))
        result = analyzer.analyze("src")
        assert len(result["harmonics"]) >= 1


class TestCordycepsMutationEngine:
    def test_import(self):
        from lab.experiments.cordyceps_mutation_engine import CordycepsMutationEngine
        assert CordycepsMutationEngine is not None

    def test_propagation(self):
        from lab.experiments.cordyceps_mutation_engine import CordycepsMutationEngine
        engine = CordycepsMutationEngine(seed=42)
        for i in range(10):
            engine.add_agent(f"a{i}", "sentinel")
        trait = engine.create_trait("test_trait", 0.3)
        engine.tick()
        result = engine.propagate_trait(trait, "a0", social_pressure=0.8)
        assert result["accepted"] + result["refused"] == 9
        assert result["immune"] == 0

    def test_immunity_accumulates(self):
        from lab.experiments.cordyceps_mutation_engine import CordycepsMutationEngine
        engine = CordycepsMutationEngine(seed=42)
        for i in range(10):
            engine.add_agent(f"a{i}", "sentinel")
        trait = engine.create_trait("t1", 0.5)
        engine.tick()
        # First propagation
        engine.propagate_trait(trait, "a0", social_pressure=0.8)
        # Second propagation should have some immune
        engine.tick()
        result = engine.propagate_trait(trait, "a0", social_pressure=0.8)
        assert result["immune"] >= 0

    def test_census(self):
        from lab.experiments.cordyceps_mutation_engine import CordycepsMutationEngine
        engine = CordycepsMutationEngine(seed=42)
        engine.add_agent("a", "sentinel")
        engine.add_agent("b", "architect")
        census = engine.population_census()
        assert census["total_agents"] == 2


class TestConstellationNarrative:
    def test_import(self):
        from lab.experiments.constellation_narrative import NarrativeWeaver, Constellation, Star
        assert NarrativeWeaver is not None

    def test_weave_produces_voices(self):
        from lab.experiments.constellation_narrative import NarrativeWeaver, Constellation, Star, Edge
        weaver = NarrativeWeaver(seed=42)
        c = Constellation(
            name="test",
            stars=[Star("A", 1, 1), Star("B", 3, 2), Star("C", 5, 1)],
            edges=[Edge("A", "B", 3), Edge("B", "C", 3)],
        )
        result = weaver.weave(c, voices=3)
        assert len(result["voices"]) == 3
        assert result["constellation"] == "test"

    def test_different_voices_differ(self):
        from lab.experiments.constellation_narrative import NarrativeWeaver, Constellation, Star, Edge
        weaver = NarrativeWeaver(seed=42)
        c = Constellation(
            name="test",
            stars=[Star("A", 1, 1), Star("B", 3, 2), Star("C", 5, 1)],
            edges=[Edge("A", "B", 3), Edge("B", "C", 3)],
        )
        result = weaver.weave(c, voices=3)
        texts = [v["text"] for v in result["voices"]]
        assert len(set(texts)) >= 2

    def test_compactness(self):
        from lab.experiments.constellation_narrative import Constellation, Star
        c = Constellation(name="compact", stars=[Star("A", 5, 5), Star("B", 5, 6)], edges=[])
        assert c.compactness > 0.5
        c2 = Constellation(name="spread", stars=[Star("A", 0, 0), Star("B", 15, 15)], edges=[])
        assert c2.compactness < c.compactness


class TestProofDensityAnalyzer:
    def test_import(self):
        from lab.experiments.proof_density_analyzer import ProofDensityAnalyzer
        assert ProofDensityAnalyzer is not None

    def test_empty_analysis(self):
        from lab.experiments.proof_density_analyzer import ProofDensityAnalyzer
        analyzer = ProofDensityAnalyzer()
        result = analyzer.analyze()
        assert result["status"] == "no_events"

    def test_clustered_events(self):
        from lab.experiments.proof_density_analyzer import ProofDensityAnalyzer, ProofEvent
        analyzer = ProofDensityAnalyzer(width=8, height=8, cell_size=2)
        for i in range(20):
            analyzer.add_event(ProofEvent(
                event_id=f"e{i}", category="test", position=(3, 3), strength=0.8, timestamp=i
            ))
        result = analyzer.analyze()
        assert result["total_events"] == 20
        assert len(result["hot_spots"]) > 0

    def test_coverage(self):
        from lab.experiments.proof_density_analyzer import ProofDensityAnalyzer, ProofEvent
        analyzer = ProofDensityAnalyzer(width=8, height=8, cell_size=2)
        for x in range(0, 8, 2):
            for y in range(0, 8, 2):
                analyzer.add_event(ProofEvent(
                    event_id=f"e{x}_{y}", category="test", position=(x, y), strength=0.5, timestamp=0
                ))
        result = analyzer.analyze()
        assert result["coverage"] > 0.5
