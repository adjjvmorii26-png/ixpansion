"""Wave 111 tests — Emergent Complexity Layer (9 modules)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_cognitive_heatmap_activate():
    from api.cognitive_heatmap import CognitiveHeatmap
    hm = CognitiveHeatmap(5, 5)
    result = hm.activate(2, 3, "thinker", 5.0)
    assert result["activated"]["heat"] > 0


def test_cognitive_heatmap_tick():
    from api.cognitive_heatmap import CognitiveHeatmap
    hm = CognitiveHeatmap(5, 5)
    hm.activate(0, 0, "a", 10.0)
    tick = hm.tick()
    assert tick["tick"] == 1


def test_knowledge_fossil_fossilize():
    from api.knowledge_fossil import KnowledgeFossilBed
    bed = KnowledgeFossilBed()
    result = bed.fossilize("ancient_algo", ["step1", "step2"], "it worked", 0.9)
    assert result["fossilized"]["quality"] == 0.9


def test_knowledge_fossil_crack():
    from api.knowledge_fossil import KnowledgeFossilBed
    bed = KnowledgeFossilBed()
    f = bed.fossilize("test_fossil", ["a", "b"], "discovery")
    result = bed.crack(f["fossilized"]["id"])
    assert "insight" in result


def test_sleep_cycle_enter():
    from api.sleep_cycle import SleepCycle
    cycle = SleepCycle()
    result = cycle.enter_phase("deep_sleep")
    assert result["phase"] == "deep_sleep"
    assert result["consolidation"] > 0.5


def test_sleep_cycle_rem_dreams():
    from api.sleep_cycle import SleepCycle
    cycle = SleepCycle()
    cycle.enter_phase("rem")
    assert len(cycle.dreams_generated) > 0
    dreams = cycle.recent_dreams()
    assert len(dreams) == 1


def test_collective_subconscious_contribute():
    from api.collective_subconscious import CollectiveSubconscious
    cs = CollectiveSubconscious()
    result = cs.contribute_symbol("flame", "agent_1", 2.0)
    assert result["symbol"]["name"] == "flame"


def test_collective_subconscious_manifest():
    from api.collective_subconscious import CollectiveSubconscious
    cs = CollectiveSubconscious()
    for i, name in enumerate(["path", "dust", "horizon", "book", "fire"]):
        cs.contribute_symbol(name, f"agent_{i}", 1.5)
    result = cs.manifest_archetype()
    assert "archetype" in result


def test_collective_subconscious_dream():
    from api.collective_subconscious import CollectiveSubconscious
    cs = CollectiveSubconscious()
    cs.contribute_symbol("void", "a", 2.0)
    cs.contribute_symbol("mirror", "b", 1.5)
    cs.contribute_symbol("whisper", "c", 1.0)
    dream = cs.collective_dream()
    assert "narrative" in dream


def test_wisdom_oracle_consult():
    from api.wisdom_oracle import WisdomOracle
    oracle = WisdomOracle()
    result = oracle.consult("What makes agents thrive?")
    assert "perspectives" in result
    assert len(result["perspectives"]) > 0


def test_wisdom_oracle_coverage():
    from api.wisdom_oracle import WisdomOracle
    oracle = WisdomOracle()
    oracle.consult("agent behavior question")
    oracle.consult("system health question")
    oracle.consult("market dynamics question")
    coverage = oracle.domain_coverage()
    assert len(coverage) >= 2


def test_gravity_well_add():
    from api.gravity_well import GravityWell
    well = GravityWell()
    result = well.add_idea("recursion", 3.0, "concept")
    assert result["added"]["mass"] >= 3.0


def test_gravity_well_merge():
    from api.gravity_well import GravityWell
    well = GravityWell()
    well.add_idea("a", 5.0)
    well.add_idea("b", 4.0)
    result = well.merge("a", "b")
    assert "merged" in result
    assert result["merged"]["mass"] >= 9.0


def test_entropy_gardener_seed():
    from api.entropy_gardener import EntropyGardener
    gardener = EntropyGardener()
    result = gardener.seed("creative_chaos", "zone_a")
    assert result["seeded"]["type"] == "creative_chaos"


def test_entropy_gardener_prune():
    from api.entropy_gardener import EntropyGardener
    gardener = EntropyGardener()
    gardener.seed("destructive_noise")
    gardener.seed("creative_chaos")
    pruned = gardener.selective_prune(0.5)
    assert len(pruned) >= 1


def test_prophecy_engine_generate():
    from api.prophecy_engine import ProphecyEngine
    engine = ProphecyEngine()
    result = engine.generate("test context")
    assert "prophecy" in result
    assert result["prophecy"]["confidence"] > 0


def test_prophecy_engine_check():
    from api.prophecy_engine import ProphecyEngine
    engine = ProphecyEngine()
    p = engine.generate("future event")
    result = engine.check(p["prophecy"]["id"], "something happened")
    assert "fulfilled" in result


def test_empathy_field_register():
    from api.empathy_field import EmpathyField
    field = EmpathyField()
    result = field.register("happy_agent", 0.8, 0.7)
    assert result["registered"]["mood"] == "positive"


def test_empathy_field_event():
    from api.empathy_field import EmpathyField
    field = EmpathyField()
    field.register("a", 0.0, 0.5)
    field.register("b", 0.0, 0.5)
    result = field.emotional_event("a", 0.8, 0.3)
    assert result["ripples"] == 1


def test_resonance_cascade_add_and_trigger():
    from api.resonance_cascade import ResonanceCascade
    rc = ResonanceCascade()
    rc.add_node("alpha", 2.0, 0.1)
    rc.add_node("beta", 2.1, 0.1)
    rc.add_node("gamma", 1.9, 0.1)
    result = rc.trigger("alpha", 5.0)
    assert result["total_amplified"] > 0
    assert len(result["steps"]) >= 1
