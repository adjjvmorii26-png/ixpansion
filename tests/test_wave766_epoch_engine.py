"""Tests for Wave 766 — epoch_engine."""
from api.wave766_epoch_engine import (
    handler, coherence_vitals, resonates_with,
    EPOCHS, _epoch_for, _era_timeline,
)


def test_contract():
    v = coherence_vitals()
    assert v["wave"] == 766
    assert v["name"] == "epoch_engine"
    assert v["status"] == "active"
    assert "module_health" in v
    assert "epoch" in v


def test_resonates():
    kins = resonates_with()
    assert "season_engine" in kins
    assert "harmony_report" in kins


def test_status():
    r = handler({"action": "status"})
    assert "current_epoch" in r
    assert "era_timeline" in r
    assert r["current_epoch"]["name"].startswith("EPOCH OF")
    assert len(r["era_timeline"]) == 7


def test_catalogue():
    r = handler({"action": "catalogue"})
    assert r["count"] == 7
    assert len(r["epochs"]) == 7
    assert "EPOCH OF SEEDING" in [e["name"] for e in r["epochs"]]
    assert "EPOCH OF SEASONS" in [e["name"] for e in r["epochs"]]


def test_bell():
    r = handler({"action": "bell"})
    assert "bell_tolled" in r
    assert r["bell_tolled"].startswith("EPOCH OF")
    assert "living" in r


def test_archive():
    r = handler({"action": "archive"})
    assert "epochs_memorialized" in r
    assert r["count"] >= 0


def test_unknown_action():
    r = handler({"action": "nonsense"})
    assert "error" in r


def test_epoch_boundaries():
    # seeding era covers waves 1-256
    assert _epoch_for(1)["name"] == "EPOCH OF SEEDING"
    assert _epoch_for(256)["name"] == "EPOCH OF SEEDING"
    assert _epoch_for(257)["name"] == "EPOCH OF WEAVING"
    # fusion era 641-704, bloom 705-764, seasons 765+
    assert _epoch_for(700)["name"] == "EPOCH OF FUSION"
    assert _epoch_for(750)["name"] == "EPOCH OF BLOOM"
    assert _epoch_for(765)["name"] == "EPOCH OF SEASONS"
    assert _epoch_for(900)["name"] == "EPOCH OF SEASONS"


def test_timeline_format():
    t = _era_timeline()
    for e in t:
        assert "name" in e and "waves" in e and "marker" in e
        assert "-now" in e["waves"] or "-" in e["waves"]
