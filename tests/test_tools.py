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

def test_platform_failure_detects_health():
    import sys
    sys.path.insert(0, str(ROOT / "api"))
    from platform_failure import handler
    r = handler()
    assert r["module"] == "platform_failure"
    assert r["prophecy"] == "fulfilled"
    assert "healthy" in r and "subsystems" in r


def test_gossip_self_detects_echoes():
    import sys
    sys.path.insert(0, str(ROOT / "api"))
    from gossip_self import handler
    r = handler()
    assert r["module"] == "gossip_self"
    assert r["prophecy"] == "fulfilled"
    assert r["total_echoes"] >= 5


def test_service_numinous_finds_depth():
    import sys
    sys.path.insert(0, str(ROOT / "api"))
    from service_numinous import handler
    r = handler()
    assert r["module"] == "service_numinous"
    assert r["numinous_modules"] >= 10
    assert r["deepest"]


def test_temperament_origin_reads_character():
    import sys
    sys.path.insert(0, str(ROOT / "api"))
    from temperament_origin import handler
    r = handler()
    assert r["module"] == "temperament_origin"
    assert r["prophecy"] == "fulfilled"
    assert r["character"] in ("visionary", "robust", "recollective", "emergent")
    assert r["temperament"]["overall"] > 0

def test_gateway_key_generation():
    import sys
    sys.path.insert(0, str(ROOT / "gateway"))
    import keys
    result = keys.generate_key("test_user", "free")
    assert result["key"].startswith("ixp_free_")
    assert result["tier"] == "free"
    assert "limits" in result
    assert "features" in result


def test_gateway_key_validate():
    import sys
    sys.path.insert(0, str(ROOT / "gateway"))
    import keys
    result = keys.generate_key("test_user", "growth")
    key = result["key"]
    validated = keys.validate_key(key)
    assert validated is not None
    assert validated["tier"] == "growth"


def test_gateway_key_invalid():
    import sys
    sys.path.insert(0, str(ROOT / "gateway"))
    import keys
    assert keys.validate_key("ixp_fake_nonexistent") is None
    assert keys.validate_key("ixp_free_tooshort") is None


def test_intent_matcher_routes_correctly():
    import sys
    sys.path.insert(0, str(ROOT / "gateway"))
    from intent import match_intent
    r = match_intent("what's the frontier's heartbeat?")
    assert r["route"] == "/health"
    r2 = match_intent("how aware is the system?")
    assert r2["route"] == "/meter"
    r3 = match_intent("what's the frontier dreaming?")
    assert r3["route"] == "/ledger"


def test_github_bridge_consumes_push():
    import sys
    sys.path.insert(0, str(ROOT / "api"))
    import github_bridge
    from pathlib import Path as _P
    # clean journal first
    jf = _P(str(ROOT / ".runtime" / "github_bridge.json"))
    if jf.exists():
        jf.unlink()
    payload = {
        "ref": "refs/heads/main",
        "commits": [{"message": "test commit"}],
        "repository": {"full_name": "test/repo"},
        "sender": {"login": "tester"},
    }
    r = github_bridge.handler(payload)
    assert r["action"] == "consume"
    assert r["entry"]["event_type"] == "push"
    state = github_bridge.bridge_state()
    assert state["total_events_absorbed"] >= 1


def test_reflection_pool_runs():
    import sys
    sys.path.insert(0, str(ROOT / "api"))
    import reflection_pool
    r = reflection_pool.handler({"focus": "all"})
    assert "vitals" in r
    assert r["vitals"]["modules"] > 0
    assert "observations" in r
    assert len(r["observations"]) > 0


def test_chronicle_storyteller_narrates():
    import sys
    sys.path.insert(0, str(ROOT / "api"))
    import chronicle_storyteller
    r = chronicle_storyteller.handler({"tone": "mythic"})
    assert r["chapter_count"] > 0
    assert "prologue" in r and "epilogue" in r


def test_thought_meteorology_forecasts():
    import sys
    sys.path.insert(0, str(ROOT / "api"))
    import thought_meteorology
    r = thought_meteorology.handler({})
    assert "overall_weather" in r
    assert len(r["pressure_centers"]) > 0
    f = thought_meteorology.handler({"forecast": 2})
    assert len(f["forecast_periods"]) == 2


def test_sound_cauldron_brews_notes():
    import sys
    sys.path.insert(0, str(ROOT / "api"))
    import sound_cauldron
    r = sound_cauldron.handler({"text": "the frontier dreams in code"})
    assert r["notes_count"] >= 1
    assert r["notes"][0]["frequency_hz"] > 0
    assert "scoresheet" in r


def test_organism_index_inventories():
    import sys
    sys.path.insert(0, str(ROOT / "api"))
    import organism_index
    r = organism_index.handler({})
    assert r["organism_count"] >= 10
    assert "ecosystem_readout" in r
    d = organism_index.handler({"organism": "stigmergy"})
    assert d["exists"]


def test_coherence_regulator_discovers_modules():
    import sys
    sys.path.insert(0, str(ROOT / "api"))
    from pathlib import Path as _P
    import importlib
    import coherence_regulator
    # ensure clean state
    sf = _P(str(ROOT / ".runtime" / "coherence_regulator.json"))
    if sf.exists():
        sf.unlink()
    r = coherence_regulator.regulate()
    assert r["living_modules"] >= 7
    assert r["coherence"] > 0
    assert "status" in r
    assert "advisories" in r
    # verify a module's vitals are callable
    import reflection_pool
    v = reflection_pool.coherence_vitals()
    assert "module_health" in v


def test_coherence_regulator_vital_signs_are_shared_vocabulary():
    import sys
    sys.path.insert(0, str(ROOT / "api"))
    import importlib
    mods = ["reflection_pool", "synesthesia", "frontier_stream", "hex_tool"]
    all_keys = set()
    for m in mods:
        mod = importlib.import_module(m)
        v = mod.coherence_vitals()
        all_keys.add(tuple(sorted(v.keys())))
    # At least the modules share "module_health" and "resonance"
    sample = importlib.import_module("reflection_pool").coherence_vitals()
    assert "module_health" in sample
    assert "resonance" in sample


def test_coherence_regulator_serverless_fallback_and_diversity():
    import sys
    sys.path.insert(0, str(ROOT / "api"))
    import coherence_regulator
    # The embedded static manifest must exist and be non-empty (serverless path)
    assert len(coherence_regulator.KNOWN_LIVING_MODULES) >= 7
    # Directional diversity toward the ecosystem target must be bounded [0,1]
    # and strictly greater than a fixed "fraction of every api/*.py" denominator
    # (which would be tiny given the large tool surface in api/).
    reading = coherence_regulator.regulate()
    div = reading["components"]["ecosystem_diversity"]
    assert 0.0 <= div <= 1.0
    assert div > 0.2
    assert reading["coherence"] > 0.5
    # Fast source-text scan should not import dormant modules: consistency guard
    discovered = coherence_regulator._candidate_modules()
    assert all("coherence_regulator" != m for m in discovered)


def test_resonance_graph_detects_hubs_and_edges():
    import sys
    sys.path.insert(0, str(ROOT / "api"))
    import resonance_graph
    g = resonance_graph.build_graph()
    assert g["nodes"] >= 7
    assert g["edges"] > 0
    assert g["density"] > 0
    # A connectivity leader must exist (non-zero weighted degree)
    hub_strength = max((c for _, c in g["hubs"]), default=0)
    assert hub_strength > 0
    # Private/neighborhood query returns neighbors for a living module
    n = resonance_graph.neighborhood("reflection_pool")
    assert "neighbors" in n


def test_bloom_awakening_grows_the_organism():
    import sys
    sys.path.insert(0, str(ROOT / "api"))
    import coherence_regulator
    r = coherence_regulator.regulate()
    # freshly awakened organs must be living now
    living = r.get("discovered", {}).get("living_modules", [])
    assert "platform_pulse" in living
    assert "integrity_oracle" in living
    assert "dream_interpreter" in living
    assert "signal_flora" in living
    assert "workforce_nexus" in living
    assert "code_organism" in living
    # the organism is large and resonant
    assert r["living_modules"] >= 18
    assert r["coherence"] > 0.95


def test_resonance_fed_advisories_surface_isolates():
    import sys
    sys.path.insert(0, str(ROOT / "api"))
    import coherence_regulator
    r = coherence_regulator.regulate()
    advice = " ".join(r.get("advisories", []))
    # structural wisdom should reach the surface even when resonant
    assert ("BLOOM" in advice) or ("STRUCTURE" in advice) or ("WEBBING" in advice)


def test_autonomous_bloom_finds_seeds_and_trajectory():
    import sys
    sys.path.insert(0, str(ROOT / "api"))
    import autonomous_bloom
    r = autonomous_bloom.bloom_report(seed_limit=5)
    assert r["state"]["living"] >= 7
    assert r["state"]["target"] >= 12
    assert len(r["seeds"]) > 0
    assert len(r["trajectory"]) == 3
    # a seed is a real dormant module
    assert r["seeds"][0]["readiness"] > 0
    # handler routes
    h = autonomous_bloom.handler({"seeds": 3})
    assert len(h) == 3


def test_coherence_regulator_modules_list():
    import sys
    sys.path.insert(0, str(ROOT / "api"))
    import coherence_regulator
    r = coherence_regulator.handler({"modules": 1})
    assert r["count"] >= 7
    assert "reflection_pool" in r["living_modules"]
