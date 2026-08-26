"""Wave 110 tests — Systems & Ecology Layer (9 modules)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_synchronicity_detector_record():
    from api.synchronicity_detector import SynchronicityDetector
    det = SynchronicityDetector()
    result = det.record_event("network", "packet_loss", {"severity": 0.8})
    assert result["recorded"]["subsystem"] == "network"


def test_synchronicity_detector_find():
    from api.synchronicity_detector import SynchronicityDetector
    det = SynchronicityDetector()
    det.record_event("network", "error", {"code": 500})
    det.record_event("database", "error", {"code": 500})
    syncs = det.get_synchronicities(0.0)
    assert isinstance(syncs, list)


def test_temperament_broker_register():
    from api.temperament_broker import TemperamentBroker
    broker = TemperamentBroker()
    result = broker.register("trader_1")
    assert "traits" in result["registered"]


def test_temperament_broker_trade():
    from api.temperament_broker import TemperamentBroker
    broker = TemperamentBroker()
    broker.register("seller_a")
    broker.register("buyer_b")
    broker.profiles["seller_a"].traits["patience"] = 0.9
    broker.profiles["buyer_b"].credits = 50.0
    result = broker.execute_trade("seller_a", "buyer_b", "patience", 0.1)
    assert "trade" in result


def test_deja_vu_engine_snapshot():
    from api.deja_vu_engine import DejaVuEngine
    engine = DejaVuEngine()
    result = engine.snapshot({"cpu": 50, "mem": 80})
    assert result["total_snapshots"] == 1


def test_deja_vu_engine_detect_loop():
    from api.deja_vu_engine import DejaVuEngine
    engine = DejaVuEngine()
    state = {"x": 1, "y": 2, "z": 3}
    engine.snapshot(state)
    engine.snapshot({"x": 1, "y": 2, "z": 4})
    engine.snapshot(state)
    loops = engine.find_loops(0.1)
    assert len(loops) >= 1


def test_talent_scout_scout():
    from api.talent_scout import TalentScout
    scout = TalentScout()
    result = scout.scout_agent("alpha", {"logic": 0.9, "creativity": 0.8}, {"pattern_detection": 0.9})
    assert "report" in result
    assert result["report"]["talent_level"] in ("low", "emerging", "promising", "exceptional")


def test_talent_scout_nurture():
    from api.talent_scout import TalentScout
    scout = TalentScout()
    scout.scout_agent("beta", {"logic": 0.7}, {"pattern_detection": 0.8})
    result = scout.nurture("beta", "advanced_research")
    assert result["nurtured"]["opportunity"] == "advanced_research"


def test_habitat_simulator_tick():
    from api.habitat_simulator import HabitatSimulator
    sim = HabitatSimulator(3, 3)
    result = sim.tick()
    assert result["tick"] == 1
    assert "season" in result


def test_habitat_simulator_introduce():
    from api.habitat_simulator import HabitatSimulator
    sim = HabitatSimulator(3, 3)
    result = sim.introduce_species("wolf", 4)
    assert result["placed"] == 4


def test_instinct_matrix_build():
    from api.instinct_matrix import InstinctMatrix
    matrix = InstinctMatrix()
    result = matrix.build_matrix("alpha", ["self_preserve", "flight_response"])
    assert len(result["instincts"]) == 2


def test_instinct_matrix_stimulus():
    from api.instinct_matrix import InstinctMatrix
    matrix = InstinctMatrix()
    matrix.build_matrix("alpha")
    fired = matrix.evaluate_stimulus("alpha", {
        "self_preserve": 0.9, "territory_mark": 0.3,
        "curiosity_snap": 0.8,
    })
    assert isinstance(fired, list)
    assert len(fired) > 0


def test_legacy_archive_archive():
    from api.legacy_archive import LegacyArchive
    archive = LegacyArchive()
    result = archive.archive("old_agent", [{"event": "deploy"}, {"event": "debug"}], {"wisdom": 0.8})
    assert result["archived"]["history_size"] == 2


def test_legacy_archive_consult():
    from api.legacy_archive import LegacyArchive
    archive = LegacyArchive()
    art = archive.archive("wise_one", [{"lesson": "patience"}], {})
    artifact_id = art["archived"]["id"]
    result = archive.consult(artifact_id, "how to be patient")
    assert result["archived_agent"] == "wise_one"


def test_phenomena_tracker_log():
    from api.phenomena_tracker import PhenomenaTracker
    tracker = PhenomenaTracker()
    result = tracker.log_phenomenon("ghost_packets", "packets appearing from nowhere", "bizarre")
    assert result["logged"]["severity"] == "bizarre"


def test_phenomena_tracker_witness():
    from api.phenomena_tracker import PhenomenaTracker
    tracker = PhenomenaTracker()
    p = tracker.log_phenomenon("time_slip", "clock jumped backward")
    result = tracker.add_witness(p["logged"]["id"], "observer_1")
    assert result["witness_count"] == 1


def test_sentience_index_record():
    from api.sentience_index import SentienceIndex
    si = SentienceIndex()
    result = si.record_signal("self_reference", 0.7, "agent_1")
    assert result["recorded"]["type"] == "self_reference"


def test_sentience_index_compute():
    from api.sentience_index import SentienceIndex
    si = SentienceIndex()
    for i in range(10):
        si.record_signal("novelty", 0.5 + i * 0.05, "system")
    index = si.compute_index()
    assert 0.0 <= index <= 1.0


def test_sentience_index_milestone():
    from api.sentience_index import SentienceIndex
    si = SentienceIndex()
    for _ in range(20):
        si.record_signal("empathy", 0.9, "system")
    assert len(si.awakening_milestones) >= 1
