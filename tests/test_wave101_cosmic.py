from __future__ import annotations
"""Wave 101 — Cosmic Infrastructure & Sentient Commerce Tests.

Tests: gravitational_pricing, speciation_engine, synesthetic_api,
chronicle_of_chaos, mycelial_commerce, warp_drive_optimizer, dream_interpreter.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── Gravitational Pricing ─────────────────────────────────────────

def test_get_price():
    from api.gravitational_pricing import GravitationalPricing
    gp = GravitationalPricing()
    result = gp.get_price("compute_hour", 1)
    assert result["unit_price"] > 0
    assert result["quantity"] == 1
    assert result["base_price"] == 1.0

def test_price_unknown_resource():
    from api.gravitational_pricing import GravitationalPricing
    gp = GravitationalPricing()
    result = gp.get_price("nonexistent")
    assert "error" in result

def test_buy_increases_demand():
    from api.gravitational_pricing import GravitationalPricing
    gp = GravitationalPricing()
    p1 = gp.get_price("compute_hour")
    gp.buy("compute_hour", 50, "heavy_user")
    p2 = gp.get_price("compute_hour")
    assert p2["unit_price"] >= p1["unit_price"]

def test_sell():
    from api.gravitational_pricing import GravitationalPricing
    gp = GravitationalPricing()
    result = gp.sell("storage_gb", 10, "seller_1")
    assert result["type"] == "sell"
    assert result["total"] > 0

def test_pricing_curve():
    from api.gravitational_pricing import GravitationalPricing
    gp = GravitationalPricing()
    curve = gp.curve("compute_hour", points=10)
    assert len(curve["curve"]) == 10
    assert curve["curve"][-1]["price"] >= curve["curve"][0]["price"]

def test_resources_available():
    from api.gravitational_pricing import RESOURCE_BASE_PRICES
    assert len(RESOURCE_BASE_PRICES) >= 7


# ── Speciation Engine ─────────────────────────────────────────────

def test_evolve():
    from api.speciation_engine import SpeciationEngine
    se = SpeciationEngine()
    sp = se.evolve("test_origin")
    assert "species_id" in sp
    assert sp["fitness"] > 0

def test_catalog():
    from api.speciation_engine import SpeciationEngine
    se = SpeciationEngine()
    se.evolve()
    se.evolve()
    cat = se.catalog()
    assert len(cat) >= 2

def test_breed():
    from api.speciation_engine import SpeciationEngine
    se = SpeciationEngine()
    a = se.evolve()
    b = se.evolve()
    child = se.breed(a["species_id"], b["species_id"])
    assert "species_id" in child
    assert child["generation"] >= 2

def test_buy_seed():
    from api.speciation_engine import SpeciationEngine
    se = SpeciationEngine()
    seed = se.buy_seed("user_1", "creativity")
    assert seed["target_trait"] == "creativity"
    assert seed["boost"] == 0.2

def test_invalid_trait_seed():
    from api.speciation_engine import SpeciationEngine
    se = SpeciationEngine()
    result = se.buy_seed("user_1", "nonexistent_trait")
    assert "error" in result

def test_phylogeny():
    from api.speciation_engine import SpeciationEngine
    se = SpeciationEngine()
    se.evolve()
    se.evolve()
    tree = se.phylogeny_tree()
    assert len(tree) >= 2


# ── Synesthetic API ───────────────────────────────────────────────

def test_to_sound():
    from api.synesthetic_api import SynestheticAPI
    api = SynestheticAPI()
    result = api.to_sound([0.3, 0.7, 0.5])
    assert "frequencies" in result
    assert len(result["frequencies"]) == 3
    assert result["key"] in ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def test_to_color():
    from api.synesthetic_api import SynestheticAPI
    api = SynestheticAPI()
    result = api.to_color([0.1, 0.5, 0.9])
    assert "palette" in result
    assert len(result["palette"]) == 3
    assert result["dominant_mood"] in ("warm", "cool", "neutral")

def test_to_texture():
    from api.synesthetic_api import SynestheticAPI
    api = SynestheticAPI()
    result = api.to_texture([0.2, 0.8])
    assert "primary_texture" in result
    assert "roughness" in result

def test_to_taste():
    from api.synesthetic_api import SynestheticAPI
    api = SynestheticAPI()
    result = api.to_taste([0.4, 0.6])
    assert "primary_taste" in result
    assert "intensity" in result

def test_full_preview():
    from api.synesthetic_api import SynestheticAPI
    api = SynestheticAPI()
    preview = api.full_preview([1, 2, 3])
    assert "sound" in preview
    assert "color" in preview
    assert "texture" in preview
    assert "taste" in preview


# ── Chronicle of Chaos ───────────────────────────────────────────

def test_record_event():
    from api.chronicle_of_chaos import ChronicleOfChaos
    ch = ChronicleOfChaos()
    result = ch.record("anomaly", "Something strange happened")
    assert "event_id" in result
    assert result["type"] == "anomaly"
    assert len(result["narrative"]) > 10

def test_record_unknown_type():
    from api.chronicle_of_chaos import ChronicleOfChaos
    ch = ChronicleOfChaos()
    result = ch.record("nonexistent", "test")
    assert result["type"] == "anomaly"

def test_edition_compilation():
    from api.chronicle_of_chaos import ChronicleOfChaos
    ch = ChronicleOfChaos()
    for i in range(6):
        ch.record("emergence", f"Event {i}")
    latest = ch.latest()
    assert "edition_number" in latest
    assert latest["event_count"] >= 5

def test_subscribe():
    from api.chronicle_of_chaos import ChronicleOfChaos
    ch = ChronicleOfChaos()
    result = ch.subscribe("reader_1")
    assert result["subscribed"]

def test_stats():
    from api.chronicle_of_chaos import ChronicleOfChaos
    ch = ChronicleOfChaos()
    ch.record("paradox", "test")
    stats = ch.stats()
    assert stats["total_events"] >= 1


# ── Mycelial Commerce ────────────────────────────────────────────

def test_list_item():
    from api.mycelial_commerce import MycelialCommerce
    mc = MycelialCommerce()
    result = mc.list_item("seller_1", "Test Item", "A test", 10.0)
    assert "listing_id" in result

def test_connect_listings():
    from api.mycelial_commerce import MycelialCommerce
    mc = MycelialCommerce()
    a = mc.list_item("s1", "Item A", "desc", 5.0)
    b = mc.list_item("s2", "Item B", "desc", 8.0)
    conn = mc.connect(a["listing_id"], b["listing_id"], "symbiotic")
    assert conn["connected"]

def test_grow_listing():
    from api.mycelial_commerce import MycelialCommerce
    mc = MycelialCommerce()
    a = mc.list_item("s1", "Grow Me", "desc", 5.0)
    result = mc.grow(a["listing_id"])
    assert result["new_depth"] == 1

def test_network_view():
    from api.mycelial_commerce import MycelialCommerce
    mc = MycelialCommerce()
    mc.list_item("s1", "A", "d", 5.0)
    mc.list_item("s2", "B", "d", 5.0)
    net = mc.network()
    assert net["total_listings"] >= 2

def test_prices():
    from api.mycelial_commerce import MycelialCommerce
    mc = MycelialCommerce()
    a = mc.list_item("s1", "Priced", "desc", 10.0)
    mc.grow(a["listing_id"])
    mc.grow(a["listing_id"])
    prices = mc.prices()
    assert len(prices) >= 1
    assert prices[0]["current_price"] >= prices[0]["base_price"]


# ── Warp Drive Optimizer ─────────────────────────────────────────

def test_set_warp():
    from api.warp_drive_optimizer import WarpDriveOptimizer
    wd = WarpDriveOptimizer()
    result = wd.set_warp("quantum_core", 5.0)
    assert result["new_warp"] == 5.0
    assert result["latency_ms"] > 0

def test_warp_capped():
    from api.warp_drive_optimizer import WarpDriveOptimizer
    wd = WarpDriveOptimizer()
    result = wd.set_warp("quantum_core", 100)
    assert result["new_warp"] <= result["max_warp"]

def test_optimize():
    from api.warp_drive_optimizer import WarpDriveOptimizer
    wd = WarpDriveOptimizer()
    result = wd.optimize()
    assert "optimized" in result
    assert len(result["optimized"]) == 8

def test_status():
    from api.warp_drive_optimizer import WarpDriveOptimizer
    wd = WarpDriveOptimizer()
    status = wd.status()
    assert len(status) == 8

def test_efficiency_report():
    from api.warp_drive_optimizer import WarpDriveOptimizer
    wd = WarpDriveOptimizer()
    wd.optimize()
    report = wd.efficiency_report()
    assert report["total_subsystems"] == 8
    assert report["avg_efficiency"] > 0

def test_emergency_stop():
    from api.warp_drive_optimizer import WarpDriveOptimizer
    wd = WarpDriveOptimizer()
    wd.set_warp("quantum_core", 8.0)
    result = wd.emergency_stop()
    assert len(result["stopped"]) == 8


# ── Dream Interpreter ────────────────────────────────────────────

def test_analyze_dream():
    from api.dream_interpreter import DreamInterpreter
    di = DreamInterpreter()
    dream = {"dream_id": "d1", "fragments": ["quantum lattice forms meaning"], "mood": "luminous"}
    result = di.analyze(dream)
    assert result["dream_id"] == "d1"
    assert len(result["insights"]) >= 1

def test_batch_analyze():
    from api.dream_interpreter import DreamInterpreter
    di = DreamInterpreter()
    dreams = [
        {"dream_id": "b1", "fragments": ["entropy rises"], "mood": "ominous"},
        {"dream_id": "b2", "fragments": ["symbiosis network grows"], "mood": "luminous"},
    ]
    results = di.batch_analyze(dreams)
    assert len(results) == 2

def test_interpretation_history():
    from api.dream_interpreter import DreamInterpreter
    di = DreamInterpreter()
    di.analyze({"dream_id": "h1", "fragments": ["test"], "mood": "serene"})
    history = di.history(5)
    assert len(history) >= 1

def test_aggregated_insights():
    from api.dream_interpreter import DreamInterpreter
    di = DreamInterpreter()
    di.analyze({"dream_id": "a1", "fragments": ["quantum paradox"], "mood": "frenetic"})
    stats = di.aggregated_insights()
    assert stats["total_insights"] >= 1

def test_mood_based_insights():
    from api.dream_interpreter import DreamInterpreter
    di = DreamInterpreter()
    result = di.analyze({"dream_id": "m1", "fragments": ["test"], "mood": "ominous"})
    mood_insights = [i for i in result["insights"] if i.get("keyword") == "mood"]
    assert len(mood_insights) >= 1


# ── Handler smoke tests ───────────────────────────────────────────

def test_all_handlers():
    from api.gravitational_pricing import handler as h1
    from api.speciation_engine import handler as h2
    from api.synesthetic_api import handler as h3
    from api.chronicle_of_chaos import handler as h4
    from api.mycelial_commerce import handler as h5
    from api.warp_drive_optimizer import handler as h6
    from api.dream_interpreter import handler as h7
    for h in [h1, h2, h3, h4, h5, h6, h7]:
        result = h({}, {})
        assert isinstance(result, (dict, list))
