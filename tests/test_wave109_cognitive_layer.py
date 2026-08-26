"""Wave 109 tests — Cognitive & Generative Layer (8 modules)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_narrative_engine_create_arc():
    from api.narrative_engine import NarrativeEngine
    engine = NarrativeEngine()
    result = engine.create_arc("The Fall of Null", "tragedy")
    assert result["arc"]["name"] == "The Fall of Null"
    assert result["arc"]["genre"] == "tragedy"


def test_narrative_engine_add_event():
    from api.narrative_engine import NarrativeEngine
    engine = NarrativeEngine()
    arc = engine.create_arc("Test Arc")
    chapter = engine.add_event(arc["arc"]["id"], "the first spark", ["agent_1"], "curious")
    assert chapter["chapter"]["event"] == "the first spark"
    assert chapter["chapter"]["actors"] == ["agent_1"]


def test_narrative_engine_summary():
    from api.narrative_engine import NarrativeEngine
    engine = NarrativeEngine()
    arc = engine.create_arc("Summary Test")
    engine.add_event(arc["arc"]["id"], "event one", ["a"], "calm")
    engine.add_event(arc["arc"]["id"], "event two", ["a", "b"], "tense")
    summary = engine.get_summary(arc["arc"]["id"])
    assert "full_narrative" in summary
    assert len(summary["story_so_far"]) == 2


def test_mutation_matrix_register():
    from api.mutation_matrix import MutationMatrix
    matrix = MutationMatrix()
    result = matrix.register_agent("agent_x", {"speed": 1.0, "stealth": 0.5})
    assert result["agent_id"] == "agent_x"
    assert "speed" in result["genome"]


def test_mutation_matrix_mutate():
    from api.mutation_matrix import MutationMatrix
    matrix = MutationMatrix()
    matrix.register_agent("m1")
    result = matrix.mutate("m1", "speed", 0.2)
    assert "mutation" in result
    assert result["mutation"]["gene"] == "speed"


def test_mutation_matrix_crossover():
    from api.mutation_matrix import MutationMatrix
    matrix = MutationMatrix()
    matrix.register_agent("parent_a")
    matrix.register_agent("parent_b")
    result = matrix.crossover("parent_a", "parent_b")
    assert "child_id" in result
    assert "genome" in result


def test_attention_field_create():
    from api.attention_field import AttentionField
    field = AttentionField()
    result = field.create_point("quantum_computing", 5.0, 3.0)
    assert result["created"]["topic"] == "quantum_computing"


def test_attention_field_direct():
    from api.attention_field import AttentionField
    field = AttentionField()
    field.create_point("topic_a")
    field.create_point("topic_b")
    result = field.direct_attention("agent_1", "topic_a", 5.0)
    assert result["directed"] == 5.0


def test_attention_field_tick():
    from api.attention_field import AttentionField
    field = AttentionField()
    field.create_point("decay_test")
    field.direct_attention("a", "decay_test", 10.0)
    tick1 = field.tick()
    assert tick1["tick"] == 1
    tick2 = field.tick()
    assert tick2["tick"] == 2


def test_reputation_network_trust():
    from api.reputation_network import ReputationNetwork
    net = ReputationNetwork()
    net.register("alice")
    net.register("bob")
    result = net.trust("alice", "bob", 0.8)
    assert result["trust"] == 0.8


def test_reputation_network_transitive():
    from api.reputation_network import ReputationNetwork
    net = ReputationNetwork()
    net.trust("a", "b", 0.9)
    net.trust("b", "c", 0.8)
    result = net.transitive_trust("a", "c")
    assert result > 0.5


def test_reputation_network_clusters():
    from api.reputation_network import ReputationNetwork
    net = ReputationNetwork()
    net.trust("a", "b", 0.9)
    net.trust("b", "c", 0.85)
    net.trust("c", "a", 0.9)
    clusters = net.trust_clusters()
    assert len(clusters) >= 1


def test_signal_flora_plant():
    from api.signal_flora import SignalFloraGarden
    garden = SignalFloraGarden()
    result = garden.plant_seed("datafern", "a quiet signal", 0, 0)
    assert result["planted"]["species"] == "datafern"


def test_signal_flora_grow():
    from api.signal_flora import SignalFloraGarden
    garden = SignalFloraGarden()
    for i in range(5):
        garden.plant_seed("bytebloom", f"signal_{i}", i, 0)
    results = garden.grow_garden()
    assert len(results) == 5


def test_signal_flora_census():
    from api.signal_flora import SignalFloraGarden
    garden = SignalFloraGarden()
    garden.plant_seed("datafern", "s1", 0, 0)
    garden.plant_seed("datafern", "s2", 1, 0)
    garden.plant_seed("signalvine", "s3", 2, 0)
    census = garden.species_census()
    assert census["datafern"] == 2
    assert census["signalvine"] == 1


def test_trait_inheritance_create():
    from api.trait_inheritance import TraitInheritanceSystem
    system = TraitInheritanceSystem()
    result = system.create_agent("alpha", {"strength": 0.9, "speed": 0.3})
    assert result["created"]["agent_id"] == "alpha"


def test_trait_inheritance_breed():
    from api.trait_inheritance import TraitInheritanceSystem
    system = TraitInheritanceSystem()
    system.create_agent("p1")
    system.create_agent("p2")
    result = system.breed("p1", "p2")
    assert "child" in result
    assert result["child"]["generation"] == 1


def test_mood_superposition_create():
    from api.mood_superposition import MoodSuperpositionSystem
    system = MoodSuperpositionSystem()
    result = system.create("agent_mood")
    assert result["created"]["collapsed"] is False
    assert "distribution" in result


def test_mood_superposition_observe():
    from api.mood_superposition import MoodSuperpositionSystem
    system = MoodSuperpositionSystem()
    created = system.create("observer_test")
    mood_id = created["created"]["id"]
    result = system.observe(mood_id, "observer_1")
    assert result["observed_state"] in ["joy", "curiosity", "dread", "calm", "confusion", "determination", "wonder", "grief"]


def test_curiosity_engine_map():
    from api.curiosity_engine import CuriosityEngine
    engine = CuriosityEngine()
    result = engine.map_region("unexplored_void", 0.9)
    assert result["mapped"]["name"] == "unexplored_void"


def test_curiosity_engine_explore():
    from api.curiosity_engine import CuriosityEngine
    engine = CuriosityEngine()
    engine.map_region("mystery_zone", 0.8)
    result = engine.explore("explorer_1", "mystery_zone")
    assert "exploration" in result


def test_pattern_sprout_sprout():
    from api.pattern_sprout import PatternSprout
    sprout = PatternSprout()
    result = sprout.sprout("fractal", "abc123", "telemetry")
    assert result["sprouted"]["type"] == "fractal"


def test_pattern_sprout_age():
    from api.pattern_sprout import PatternSprout
    sprout = PatternSprout()
    for i in range(5):
        sprout.sprout("cycle", f"pat_{i}")
    results = sprout.age_all()
    assert len(results) == 5
