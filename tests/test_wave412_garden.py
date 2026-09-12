"""Tests for Wave 412 Garden Realm."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))
import wave412_garden as wg

def test_garden_grows():
    garden = wg.grow_garden()
    assert garden["module"] == "wave412_garden"
    assert "gardens" in garden
    assert len(garden["gardens"]) == 3
    assert garden["bloom_state"] == "blooming"

def test_status_after_grow():
    wg.handler({"action": "grow"})
    status = wg.handler({"action": "status"})
    assert status["bloom_state"] in ("blooming", "full_bloom")

def test_topology():
    wg.handler({"action": "grow"})
    topo = wg.handler({"action": "topology"})
    assert topo["wave"] == 412
    assert topo["realm"] == "garden"
    assert topo["graph_stats"]["garden_count"] == 3

def test_bloom():
    wg.handler({"action": "grow"})
    bloom = wg.handler({"action": "bloom"})
    assert bloom["bloomed"] is True
    assert bloom["total_blooms"] >= 1

def test_cycle():
    wg.handler({"action": "grow"})
    cycle = wg.handler({"action": "cycle"})
    assert cycle["season"] in ("spring", "summer", "autumn", "winter")

def test_coherence():
    vitals = wg.coherence_vitals()
    assert vitals["status"] == "active"
    assert vitals["wave"] == 412

def test_handler_actions():
    result = wg.handler({"action": "bogus"})
    assert "error" in result
    assert "valid" in result

def test_garden_persists():
    wg.handler({"action": "grow"})
    report_path = Path(__file__).parent.parent / "data" / "wave412_garden.json"
    assert report_path.exists()
    data = json.loads(report_path.read_text())
    assert "gardens" in data
