"""Wave 108 tests — Sensory & Environmental Layer (8 modules)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_memory_crystals_store():
    from api.memory_crystals import MemoryLattice
    lattice = MemoryLattice()
    result = lattice.store("agent_1", "the first memory", 0.8)
    assert result["stored"]["agent_id"] == "agent_1"
    assert result["stored"]["emotional_weight"] == 0.8


def test_memory_crystals_search():
    from api.memory_crystals import MemoryLattice
    lattice = MemoryLattice()
    lattice.store("a", "bright morning light", 0.9)
    lattice.store("b", "dark evening shadow", 0.2)
    results = lattice.search_by_resonance({"emotional_facet": 0.9})
    assert len(results) > 0
    assert results[0]["match_score"] > 0


def test_memory_crystals_crystallize():
    from api.memory_crystals import MemoryLattice
    lattice = MemoryLattice()
    lattice.store("x", "crystalline thought")
    results = lattice.crystallize_all()
    assert len(results) == 1
    assert results[0]["age"] == 1


def test_shadow_ledger_record():
    from api.shadow_ledger import ShadowLedger
    ledger = ShadowLedger()
    result = ledger.record("deploy_v2", ["rollback", "pause", "debug"])
    assert result["recorded"]["action_taken"] == "deploy_v2"
    assert len(result["recorded"]["alternatives_rejected"]) == 3


def test_shadow_ledger_regret():
    from api.shadow_ledger import ShadowLedger
    ledger = ShadowLedger()
    ledger.record("attack", ["defend", "flee", "negotiate"])
    ledger.record("retreat", ["charge", "hold", "flank"])
    result = ledger.analyze_regret(5)
    assert result["entries_analyzed"] == 2
    assert "average_regret" in result


def test_shadow_ledger_counterfactual():
    from api.shadow_ledger import ShadowLedger
    ledger = ShadowLedger()
    ledger.record("plan_a", ["plan_b", "plan_c"])
    ledger.record("plan_d", ["plan_b", "plan_e"])
    shadows = ledger.find_counterfactual("plan_b")
    assert len(shadows) == 2


def test_semantic_weather_conditions():
    from api.semantic_weather import SemanticWeatherSystem
    weather = SemanticWeatherSystem()
    conditions = weather.current_conditions()
    assert "weather_type" in conditions
    assert conditions["weather_type"] in ("clear", "foggy", "stormy", "rainy", "sunny", "blizzard", "aurora")


def test_semantic_weather_inject_storm():
    from api.semantic_weather import SemanticWeatherSystem
    weather = SemanticWeatherSystem()
    result = weather.inject_storm(50.0)
    assert result["wind_speed"] > 0
    assert result["event"] == "contradiction_storm_approaching"


def test_semantic_weather_forecast():
    from api.semantic_weather import SemanticWeatherSystem
    weather = SemanticWeatherSystem()
    forecast = weather.forecast_next(3)
    assert len(forecast) == 3
    assert all("weather_type" in f for f in forecast)


def test_semantic_weather_advice():
    from api.semantic_weather import SemanticWeatherSystem
    weather = SemanticWeatherSystem()
    advice = weather.advice_for_agents()
    assert "advice" in advice
    assert "current_weather" in advice


def test_hive_constructor_place():
    from api.hive_constructor import HiveConstructor
    hive = HiveConstructor()
    result = hive.place_block("builder_1", "foundation", (0, 0, 0))
    assert result["placed"]["type"] == "foundation"


def test_hive_constructor_integrity():
    from api.hive_constructor import HiveConstructor
    hive = HiveConstructor()
    hive.place_block("a", "foundation", (0, 0, 0))
    hive.place_block("a", "pillar", (1, 0, 0))
    hive.place_block("a", "arch", (0, 1, 0))
    integrity = hive.structural_integrity()
    assert integrity["total_blocks"] == 3
    assert integrity["integrity_score"] > 0


def test_hive_constructor_blueprint():
    from api.hive_constructor import HiveConstructor
    hive = HiveConstructor()
    for i in range(5):
        hive.place_block("builder", "pillar", (i, 0, 0))
    result = hive.blueprint_emergence()
    assert result["emerging_pattern"] in ("cathedral", "colonnade", "aqueduct", "observatory", "network", "garden")


def test_echo_chamber_send():
    from api.echo_chamber import EchoChamber
    chamber = EchoChamber()
    result = chamber.send("agent_1", "the truth is out there")
    assert result["sent"]["source"] == "agent_1"
    assert result["sent"]["alive"] is True


def test_echo_chamber_bounce():
    from api.echo_chamber import EchoChamber
    chamber = EchoChamber()
    sent = chamber.send("a", "hello world")
    msg_id = sent["sent"]["id"]
    result = chamber.bounce_message(msg_id, "amplify", 0.8)
    assert "transformation" in result
    assert result["message"]["bounces"] == 1


def test_echo_chamber_bounce_all():
    from api.echo_chamber import EchoChamber
    chamber = EchoChamber()
    chamber.send("a", "msg1")
    chamber.send("b", "msg2")
    results = chamber.bounce_all(strength=0.5)
    assert len(results) == 2


def test_evolutionary_pressure_introduce():
    from api.evolutionary_pressure import EvolutionaryPressureSystem
    system = EvolutionaryPressureSystem()
    result = system.introduce("organism_1", 1.0, ["fast", "adaptive"])
    assert result["introduced"]["agent_id"] == "organism_1"


def test_evolutionary_pressure_apply():
    from api.evolutionary_pressure import EvolutionaryPressureSystem
    system = EvolutionaryPressureSystem()
    system.introduce("p1", 1.0)
    system.introduce("p2", 0.8)
    result = system.apply_global_pressure("scarcity", 0.3)
    assert "results" in result
    assert len(result["results"]) == 2


def test_evolutionary_pressure_reproduce():
    from api.evolutionary_pressure import EvolutionaryPressureSystem
    system = EvolutionaryPressureSystem()
    system.introduce("parent", 1.5, ["strong"])
    system.introduce("weak", 0.3)
    offspring = system.select_and_reproduce(top_n=1)
    assert len(offspring) >= 1
    assert offspring[0]["agent_id"].startswith("parent")


def test_dream_interpreter_interpret():
    from api.dream_interpreter_api import DreamInterpreter
    interp = DreamInterpreter()
    result = interp.interpret("I walked through a vast ocean of fire under a stormy clock tower")
    assert len(result["metaphors"]) > 0
    assert "ocean" in [m["word"] for m in result["metaphors"]]


def test_dream_interpreter_batch():
    from api.dream_interpreter_api import DreamInterpreter
    interp = DreamInterpreter()
    results = interp.batch_interpret([
        {"text": "a garden of mirrors", "agent_id": "d1"},
        {"text": "a spider on a mountain of keys", "agent_id": "d2"},
    ])
    assert len(results) == 2


def test_consensus_reality_propose():
    from api.consensus_reality import ConsensusReality
    reality = ConsensusReality()
    result = reality.propose("dark_matter_api", "an API that processes nothing", "observer_1")
    assert result["proposed"]["exists"] is False


def test_consensus_reality_vote_to_exist():
    from api.consensus_reality import ConsensusReality
    reality = ConsensusReality()
    p = reality.propose("real_thing", "something real", "a")
    eid = p["proposed"]["id"]
    reality.vote(eid, "v1", True)
    reality.vote(eid, "v2", True)
    reality.vote(eid, "v3", True)
    detail = reality.entity_detail(eid)
    assert detail["exists"] is True
    assert detail["believers"] == 3


def test_consensus_reality_vote_to_dissolve():
    from api.consensus_reality import ConsensusReality
    reality = ConsensusReality()
    p = reality.propose("fading", "something fading", "a")
    eid = p["proposed"]["id"]
    reality.vote(eid, "v1", True)
    reality.vote(eid, "v2", True)
    assert reality.entities[eid].exists
    reality.vote(eid, "v3", False)
    reality.vote(eid, "v4", False)
    reality.vote(eid, "v5", False)
    detail = reality.entity_detail(eid)
    assert detail["exists"] is False
