from __future__ import annotations
"""Wave 99 — Emergent Intelligence & Living Systems Tests.

Tests: cognitive_resonance, temporal_market, entropy_auction,
dream_synthesis, symbiosis_network, paradox_marketplace, memory_palace.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── Cognitive Resonance ───────────────────────────────────────────

def test_agent_profiles_exist():
    from api.cognitive_resonance import AGENT_PROFILES
    assert len(AGENT_PROFILES) == 6
    assert "scout_alpha" in AGENT_PROFILES

def test_measure_pair():
    from api.cognitive_resonance import CognitiveResonanceEngine
    engine = CognitiveResonanceEngine()
    result = engine.measure_pair("scout_alpha", "oracle_epsilon")
    assert "resonance" in result
    assert 0 <= result["resonance"] <= 1
    assert result["resonance_level"] in ("strong", "moderate", "weak")

def test_measure_unknown_pair():
    from api.cognitive_resonance import CognitiveResonanceEngine
    engine = CognitiveResonanceEngine()
    result = engine.measure_pair("ghost_a", "ghost_b")
    assert "error" in result

def test_form_cluster():
    from api.cognitive_resonance import CognitiveResonanceEngine
    engine = CognitiveResonanceEngine()
    cluster = engine.form_cluster(
        ["scout_alpha", "analyst_beta", "weaver_delta"],
        name="test_team"
    )
    assert "cluster_id" in cluster
    assert cluster["name"] == "test_team"
    assert cluster["avg_resonance"] > 0

def test_cluster_too_small():
    from api.cognitive_resonance import CognitiveResonanceEngine
    engine = CognitiveResonanceEngine()
    result = engine.form_cluster(["scout_alpha"])
    assert "error" in result

def test_synthesize():
    from api.cognitive_resonance import CognitiveResonanceEngine
    engine = CognitiveResonanceEngine()
    cluster = engine.form_cluster(["scout_alpha", "analyst_beta"], name="duo")
    synth = engine.synthesize(cluster["cluster_id"], problem="find patterns")
    assert "synthesis_power" in synth
    assert synth["synthesis_power"] >= 0

def test_list_clusters():
    from api.cognitive_resonance import CognitiveResonanceEngine
    engine = CognitiveResonanceEngine()
    engine.form_cluster(["sentinel_gamma", "kintsugi_zeta"])
    clusters = engine.list_clusters()
    assert len(clusters) >= 1

def test_resonance_history():
    from api.cognitive_resonance import CognitiveResonanceEngine
    engine = CognitiveResonanceEngine()
    engine.measure_pair("scout_alpha", "analyst_beta")
    history = engine.history_log(5)
    assert len(history) >= 1


# ── Temporal Market ───────────────────────────────────────────────

def test_submit_prediction():
    from api.temporal_market import TemporalMarket
    m = TemporalMarket()
    pred = m.predict("trader_1", 10, {"count": 100}, stake_credits=50)
    assert "market_id" in pred
    assert pred["stake"] == 50
    assert pred["horizon_cycles"] == 10

def test_prediction_min_stake():
    from api.temporal_market import TemporalMarket
    m = TemporalMarket()
    result = m.predict("trader", 5, {"x": 1}, stake_credits=0.5)
    assert "error" in result

def test_bet_on_market():
    from api.temporal_market import TemporalMarket
    m = TemporalMarket()
    pred = m.predict("trader_1", 5, {"a": 1}, stake_credits=10)
    bet = m.bet(pred["market_id"], "trader_2", "for", 20)
    assert bet["pool_total"] == 30

def test_settle_market():
    from api.temporal_market import TemporalMarket
    m = TemporalMarket()
    pred = m.predict("trader_1", 3, {"x": 50}, stake_credits=10)
    m.bet(pred["market_id"], "trader_2", "against", 15)
    result = m.settle(pred["market_id"])
    assert "accuracy" in result
    assert result["pool_total"] == 25

def test_list_markets():
    from api.temporal_market import TemporalMarket
    m = TemporalMarket()
    m.predict("t1", 5, {"a": 1}, stake_credits=5)
    markets = m.list_markets("open")
    assert len(markets) >= 1


# ── Entropy Auction ───────────────────────────────────────────────

def test_create_auction():
    from api.entropy_auction import EntropyAuction
    ea = EntropyAuction()
    auc = ea.create_auction("quantum_core", "system", max_chaos=0.5)
    assert "auction_id" in auc
    assert auc["max_chaos"] == 0.5

def test_place_bid():
    from api.entropy_auction import EntropyAuction
    ea = EntropyAuction()
    auc = ea.create_auction("entropy_field", "system")
    bid = ea.bid(auc["auction_id"], "user_1", 100, chaos_level=0.3)
    assert bid["bid_amount"] == 100
    assert bid["position"] == 1

def test_bid_exceeds_max_chaos():
    from api.entropy_auction import EntropyAuction
    ea = EntropyAuction()
    auc = ea.create_auction("sub", "system", max_chaos=0.3)
    result = ea.bid(auc["auction_id"], "user_1", 50, chaos_level=0.8)
    assert "error" in result

def test_resolve_auction():
    from api.entropy_auction import EntropyAuction
    ea = EntropyAuction()
    auc = ea.create_auction("lattice", "system")
    ea.bid(auc["auction_id"], "r1", 100, chaos_level=0.2)
    ea.bid(auc["auction_id"], "r2", 250, chaos_level=0.4)
    result = ea.resolve(auc["auction_id"])
    assert result["winner"] == "r2"
    assert result["winning_bid"] == 250
    assert len(result["outcomes"]) >= 1

def test_resolve_empty():
    from api.entropy_auction import EntropyAuction
    ea = EntropyAuction()
    auc = ea.create_auction("empty", "system")
    result = ea.resolve(auc["auction_id"])
    assert result["status"] == "expired"


# ── Dream Synthesis ───────────────────────────────────────────────

def test_generate_dream():
    from api.dream_synthesis import DreamSynthesis
    ds = DreamSynthesis()
    dream = ds.generate("user_1", theme="cosmos")
    assert "dream_id" in dream
    assert dream["mood"] in ["luminous", "melancholic", "frenetic", "serene", "ominous", "playful"]
    assert len(dream["fragments"]) >= 3

def test_dream_gallery():
    from api.dream_synthesis import DreamSynthesis
    ds = DreamSynthesis()
    ds.generate("u1")
    ds.generate("u2")
    gallery = ds.gallery(5)
    assert len(gallery) >= 1

def test_subscribe_dreams():
    from api.dream_synthesis import DreamSynthesis
    ds = DreamSynthesis()
    result = ds.subscribe("user_1", "daily")
    assert result["subscribed"]
    assert result["frequency"] == "daily"

def test_dream_stats():
    from api.dream_synthesis import DreamSynthesis
    ds = DreamSynthesis()
    ds.generate("u1")
    ds.subscribe("u2")
    stats = ds.dream_stats()
    assert stats["total_dreams"] >= 1
    assert stats["total_subscribers"] >= 1


# ── Symbiosis Network ────────────────────────────────────────────

def _get_or_create_pair(net, a, b):
    """Get existing relationship or create new one."""
    pair_key = "-".join(sorted([a, b]))
    if pair_key in net.relationships:
        return pair_key
    result = net.pair(a, b)
    if "pair_key" in result:
        return result["pair_key"]
    return result.get("existing", pair_key)

def test_form_symbiosis():
    from api.symbiosis_network import SymbiosisNetwork
    net = SymbiosisNetwork()
    pk = _get_or_create_pair(net, "oracle_epsilon", "kintsugi_zeta")
    rel = net.relationships[pk]
    assert rel["mutual_benefit"] >= 0

def test_confirm_symbiosis():
    from api.symbiosis_network import SymbiosisNetwork
    net = SymbiosisNetwork()
    pk = _get_or_create_pair(net, "oracle_epsilon", "kintsugi_zeta")
    result = net.confirm(pk)
    assert result.get("status") == "active"

def test_trade_capability():
    from api.symbiosis_network import SymbiosisNetwork
    net = SymbiosisNetwork()
    pk = _get_or_create_pair(net, "oracle_epsilon", "kintsugi_zeta")
    net.confirm(pk)
    trade = net.trade(pk, "oracle_epsilon", "prediction")
    assert trade["trade_count"] >= 1

def test_network_view():
    from api.symbiosis_network import SymbiosisNetwork
    net = SymbiosisNetwork()
    _get_or_create_pair(net, "oracle_epsilon", "kintsugi_zeta")
    view = net.network_view()
    assert len(view) >= 1

def test_health_report():
    from api.symbiosis_network import SymbiosisNetwork
    net = SymbiosisNetwork()
    _get_or_create_pair(net, "oracle_epsilon", "kintsugi_zeta")
    health = net.health_report()
    assert "total_relationships" in health
    assert health["total_relationships"] >= 1

def test_cannot_self_symbiosis():
    from api.symbiosis_network import SymbiosisNetwork
    net = SymbiosisNetwork()
    result = net.pair("scout_alpha", "scout_alpha")
    assert "error" in result


# ── Paradox Marketplace ──────────────────────────────────────────

def test_submit_paradox():
    from api.paradox_marketplace import ParadoxMarketplace
    pm = ParadoxMarketplace()
    result = pm.submit("user_1", "A is true", "A is false", domain="logic")
    assert "paradox_id" in result
    assert result["tension"] >= 0

def test_resolve_paradox():
    from api.paradox_marketplace import ParadoxMarketplace
    pm = ParadoxMarketplace()
    p = pm.submit("u1", "deterministic", "random", bounty=25)
    result = pm.resolve(p["paradox_id"], "resolver_1", "both are true", "synthesis")
    assert "resolved" in result

def test_list_open_paradoxes():
    from api.paradox_marketplace import ParadoxMarketplace
    pm = ParadoxMarketplace()
    pm.submit("u1", "fast", "slow")
    open_p = pm.list_open()
    assert len(open_p) >= 1

def test_paradox_stats():
    from api.paradox_marketplace import ParadoxMarketplace
    pm = ParadoxMarketplace()
    pm.submit("u1", "x", "not x")
    stats = pm.stats()
    assert "total_paradoxes" in stats
    assert stats["total_paradoxes"] >= 1


# ── Memory Palace ─────────────────────────────────────────────────

def test_create_palace():
    from api.memory_palace import MemoryPalace
    mp = MemoryPalace()
    palace = mp.create("user_1", "My Palace")
    assert "palace_id" in palace
    assert palace["name"] == "My Palace"

def test_add_room():
    from api.memory_palace import MemoryPalace
    mp = MemoryPalace()
    palace = mp.create("user_1")
    room = mp.add_room(palace["palace_id"], "experience", "Events")
    assert "room_id" in room
    assert room["type"] == "experience"

def test_store_memory():
    from api.memory_palace import MemoryPalace
    mp = MemoryPalace()
    palace = mp.create("user_1")
    room = mp.add_room(palace["palace_id"], "learning")
    result = mp.store(palace["palace_id"], room["room_id"],
                      "Pattern detected in quantum data",
                      tags=["quantum", "pattern"])
    assert "memory_id" in result

def test_recall_memory():
    from api.memory_palace import MemoryPalace
    mp = MemoryPalace()
    palace = mp.create("user_1")
    room = mp.add_room(palace["palace_id"], "experience")
    mp.store(palace["palace_id"], room["room_id"],
             "Quantum tunneling observed", tags=["quantum"])
    mp.store(palace["palace_id"], room["room_id"],
             "Economy growing steadily", tags=["economy"])
    results = mp.recall(palace["palace_id"], "quantum")
    assert len(results) == 1
    assert "quantum" in results[0]["content"].lower()

def test_palace_map():
    from api.memory_palace import MemoryPalace
    mp = MemoryPalace()
    palace = mp.create("user_1", "Map Test")
    mp.add_room(palace["palace_id"], "experience")
    mp.add_room(palace["palace_id"], "dream")
    mp_map = mp.palace_map(palace["palace_id"])
    assert len(mp_map["rooms"]) == 2

def test_palace_stats():
    from api.memory_palace import MemoryPalace
    mp = MemoryPalace()
    palace = mp.create("user_1")
    mp.add_room(palace["palace_id"], "experience")
    stats = mp.palace_stats(palace["palace_id"])
    assert stats["total_rooms"] == 1


# ── Handler smoke tests ───────────────────────────────────────────

def test_all_handlers():
    from api.cognitive_resonance import handler as h1
    from api.temporal_market import handler as h2
    from api.entropy_auction import handler as h3
    from api.dream_synthesis import handler as h4
    from api.symbiosis_network import handler as h5
    from api.paradox_marketplace import handler as h6
    from api.memory_palace import handler as h7
    for h in [h1, h2, h3, h4, h5, h6, h7]:
        result = h({}, {})
        assert isinstance(result, (dict, list))
