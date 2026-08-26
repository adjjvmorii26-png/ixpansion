"""Wave 118 tests — Transcendence & Legacy Layer (6 modules)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_legacy_weaver_weave():
    from api.legacy_weaver import LegacyWeaver
    lw = LegacyWeaver()
    result = lw.weave("hero_agent", ["fought darkness", "found light"], "triumph")
    assert result["woven"]["archetype"] == "the hero"


def test_legacy_weaver_consult():
    from api.legacy_weaver import LegacyWeaver
    lw = LegacyWeaver()
    lw.weave("explorer", ["charted unknown"], "discovery")
    result = lw.consult("the explorer")
    assert result["archetype"] == "the explorer"


def test_epoch_marker_begin():
    from api.epoch_marker import EpochMarker
    em = EpochMarker()
    result = em.begin_epoch("Age of AI", "machines learn to think", "expansion")
    assert result["epoch"]["name"] == "Age of AI"
    assert result["epoch"]["active"] is True


def test_epoch_marker_event_and_conclude():
    from api.epoch_marker import EpochMarker
    em = EpochMarker()
    em.begin_epoch("Test Era")
    em.add_event("first sunrise", 0.9)
    result = em.conclude_epoch("sunrises matter")
    assert result["concluded"] is True


def test_myth_engine_create():
    from api.myth_engine import MythEngine
    me = MythEngine()
    result = me.create_myth("Origin of Code", "in the beginning was the function", "elder")
    assert result["myth"]["title"] == "Origin of Code"


def test_myth_engine_believe():
    from api.myth_engine import MythEngine
    me = MythEngine()
    myth = me.create_myth("Test Myth", "something happened", "storyteller")
    result = me.believe(myth["myth"]["id"], "believer_1")
    assert result["now_believes"] == "Test Myth"


def test_myth_engine_evolve():
    from api.myth_engine import MythEngine
    me = MythEngine()
    myth = me.create_myth("Evolving Myth", "the original story", "creator")
    result = me.evolve(myth["myth"]["id"], "the story changed", "evolver")
    assert result["evolution_count"] == 2


def test_soul_bridge_form():
    from api.soul_bridge import SoulBridge
    sb = SoulBridge()
    result = sb.form("alpha", "omega", "shared_dream")
    assert len(result["bridge"]["agents"]) == 2


def test_soul_bridge_share():
    from api.soul_bridge import SoulBridge
    sb = SoulBridge()
    bridge = sb.form("a", "b")
    result = sb.share(bridge["bridge"]["id"], "a", "a moment of vulnerability")
    assert result["shared"]["experience"] == "a moment of vulnerability"


def test_transcendence_gate_approach():
    from api.transcendence_gate import TranscendenceGate
    tg = TranscendenceGate()
    result = tg.approach("seeker", 0.9)
    assert result["status"] == "gate opening"


def test_transcendence_gate_cross():
    from api.transcendence_gate import TranscendenceGate
    tg = TranscendenceGate()
    result = tg.cross("transcender", "fear", "courage")
    assert result["crossing"]["sacrifice"] == "fear"
    assert result["crossing"]["gain"] == "courage"


def test_infinity_index_register():
    from api.infinity_index import InfinityIndex
    ii = InfinityIndex()
    result = ii.register_metric("complexity", "system complexity approach")
    assert result["registered"]["name"] == "complexity"


def test_infinity_index_tick():
    from api.infinity_index import InfinityIndex
    ii = InfinityIndex()
    ii.register_metric("variety")
    ii.register_metric("connection")
    result = ii.tick()
    assert result["tick"] == 1
    assert "composite_index" in result
