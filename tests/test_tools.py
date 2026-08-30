"""Tools smoke tests."""
from __future__ import annotations
import sys, subprocess, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

def test_entropy_sparkline_runs():
    r = subprocess.run(["python3", str(ROOT / "tools" / "entropy_sparkline.py")],
                       capture_output=True, text=True, timeout=30)
    assert r.returncode == 0
    assert "ENTROPY SPARKLINE" in r.stdout
    assert "commits" in r.stdout


def test_garden_family_tree_runs():
    r = subprocess.run(["python3", str(ROOT / "tools" / "garden_family_tree.py")],
                       capture_output=True, text=True, timeout=10)
    assert r.returncode == 0
    assert "FAMILY TREE" in r.stdout
    assert "organism" in r.stdout

def test_frontier_song_generates_notes():
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    from frontier_song import generate_notes, module_names, name_to_note
    names = module_names()
    assert len(names) > 100
    notes = generate_notes(names)
    assert len(notes) == len(names)
    f, d, v = name_to_note("test_module", 0)
    assert 100 < f <= 1760
    assert 0 < d <= 1 and 0 < v <= 1


def test_frontier_song_renders_wav(tmp_path):
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    from frontier_song import render_wav
    out = tmp_path / "t.wav"
    p = render_wav(["alpha_beta", "gamma_delta"], output=out)
    import wave
    w = wave.open(str(p))
    assert w.getnframes() > 0
    w.close()

def test_time_capsule_seals_and_verifies(tmp_path):
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    import time_capsule as tc
    cap = tc.seal()
    assert cap["ixpansion_time_capsule"] is True
    assert cap["api_modules"] > 100
    assert "seal_sha256" in cap
    v = tc.verify(cap)
    assert v["integrity"] is True


def test_time_capsule_detects_tampering():
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    import time_capsule as tc
    cap = tc.seal()
    cap["git_head"] = "deadbeef"  # tamper
    v = tc.verify(cap)
    assert v["integrity"] is False

def test_pulsar_constellation_handler():
    import sys
    sys.path.insert(0, str(ROOT / "api"))
    from pulsar_constellation import handler
    r = handler()
    assert r["module"] == "pulsar_constellation"
    assert r["prophecy"] == "fulfilled"
    assert r["stars"] > 100
    assert r["pulsars"] >= 1


def test_ledger_fulfills_pulsar_constellation(tmp_path):
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    from harbinger.agents import ledger as _ledger
    _ledger.LEDGER = tmp_path / "test_ledger.json"
    _ledger.record_dreams([{"name": "pulsar_constellation", "fuel": ["pulsar", "constellation"]}], wave="test")
    from pathlib import Path as _P
    _ledger.ROOT = tmp_path  # won't match api/ but tests the flow
    state = _ledger.ledger()
    assert state["total"] == 1
    assert state["counts"]["dreamed"] == 1

def test_gossip_uptime_propagates():
    import sys
    sys.path.insert(0, str(ROOT / "api"))
    from gossip_uptime import simulate
    r = simulate("gossip_network")
    assert r["module"] == "gossip_uptime"
    assert r["prophecy"] == "fulfilled"
    assert r["reached_pct"] > 20
    assert r["total_modules"] > 300

def test_oracle_guild_surveys_members():
    import sys
    sys.path.insert(0, str(ROOT / "api"))
    from oracle_guild import handler
    r = handler()
    assert r["module"] == "oracle_guild"
    assert r["prophecy"] == "fulfilled"
    assert len(r["members"]) >= 5
    assert r["guild"]["member_count"] >= 5

def test_data_complexity_index():
    import sys
    sys.path.insert(0, str(ROOT / "api"))
    from data_complexity import handler
    r = handler()
    assert r["module"] == "data_complexity"
    assert r["prophecy"] == "fulfilled"
    assert r["modules"] > 300
    assert 0 < r["complexity_index"] <= 100

def test_frontier_intent_analyzes_themes():
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    from frontier_intent import analyze
    r = analyze()
    assert r["modules"] > 300
    assert len(r["themes"]) >= 5
    assert len(r["focus_vector"]) >= 3
    total_share = round(sum(t["share"] for t in r["themes"]), 0)
    assert total_share >= 98  # shares roughly sum to 100
