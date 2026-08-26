"""Wave 127 -- Entropic Economics Layer tests."""
from __future__ import annotations

from api.entropy_exchange import EntropyExchange, EntropyCommodity
from api.complexity_currency import ComplexityCurrency, ComplexityCoin
from api.chaos_auction import ChaosAuction, AuctionLot
from api.order_futures import OrderFuturesMarket, OrderFuture
from api.gravitational_pricing import GravitationalPricingEngine, GravitationalItem
from api.temporal_arbitrage import TemporalArbitrageEngine, ArbitrageOpportunity
from api.sponsored_experiments import SponsoredExperimentsEngine, Experiment
from api.simulation_as_service import SimulationAsService, SimulationRun


class TestEntropyExchange:
    def test_list_and_trade(self):
        ex = EntropyExchange()
        ex.list_commodity("wild_chaos", 0.9)
        ex.list_commodity("pure_order", 0.1)
        trade = ex.trade("buyer_A", "seller_B", "wild_chaos")
        assert trade["type"] == "chaos"
        assert trade["price"] > 0

    def test_market_value(self):
        ex = EntropyExchange()
        ex.list_commodity("c1", 0.5)
        ex.list_commodity("c2", 0.8)
        assert ex.market_value() > 0

    def test_status(self):
        ex = EntropyExchange()
        ex.list_commodity("c", 0.5)
        s = ex.status()
        assert s["commodities"] == 1


class TestComplexityCurrency:
    def test_mint_and_transfer(self):
        cc = ComplexityCurrency()
        coin = cc.mint(10.0, 0.7)
        assert coin.exchange_rate > 0
        record = cc.transfer("A", "B", coin)
        assert record["from"] == "A"

    def test_total_supply(self):
        cc = ComplexityCurrency()
        cc.mint(5.0, 0.5)
        cc.mint(3.0, 0.8)
        assert cc.total_supply() == 8.0

    def test_status(self):
        cc = ComplexityCurrency()
        cc.mint(1.0, 0.5)
        s = cc.status()
        assert s["total_coins"] == 1


class TestChaosAuction:
    def test_list_bid_close(self):
        ca = ChaosAuction()
        lot = ca.list_lot("Entropy Storm", 0.9, reserve=50.0)
        ca.place_bid(lot.id, "Bidder1", 60.0)
        result = ca.close_lot(lot.id)
        assert result["sold"] is True
        assert result["winner"] == "Bidder1"

    def test_reserve_not_met(self):
        ca = ChaosAuction()
        lot = ca.list_lot("Weak Signal", 0.3, reserve=100.0)
        ca.place_bid(lot.id, "B1", 10.0)
        result = ca.close_lot(lot.id)
        assert result["sold"] is False

    def test_status(self):
        ca = ChaosAuction()
        ca.list_lot("L", 0.5)
        s = ca.status()
        assert s["total_lots"] == 1


class TestOrderFutures:
    def test_create_and_buy(self):
        m = OrderFuturesMarket()
        fut = m.create_future("Q4 Stability", 0.8)
        result = m.buy(fut.id, "buyer_X")
        assert result["buyer"] == "buyer_X"

    def test_tick(self):
        m = OrderFuturesMarket()
        m.create_future("F1", 0.5)
        active = m.tick()
        assert active >= 1

    def test_status(self):
        m = OrderFuturesMarket()
        m.create_future("F1", 0.5)
        s = m.status()
        assert s["total_futures"] == 1


class TestGravitationalPricing:
    def test_add_and_purchase(self):
        gp = GravitationalPricingEngine()
        gp.add_item("ModuleA", 10.0)
        result = gp.purchase("ModuleA", "buyer")
        assert result["price"] > 10.0

    def test_connect_increases_price(self):
        gp = GravitationalPricingEngine()
        gp.add_item("A", 5.0)
        gp.add_item("B", 5.0)
        price_before = gp._items["A"].price
        gp.connect_items("A", "B")
        assert gp._items["A"].price > price_before

    def test_status(self):
        gp = GravitationalPricingEngine()
        gp.add_item("X")
        s = gp.status()
        assert s["total_items"] == 1


class TestTemporalArbitrage:
    def test_record_and_detect(self):
        ta = TemporalArbitrageEngine()
        for p in [10.0, 5.0, 15.0, 3.0]:
            ta.record_price("widget", p)
        result = ta.detect("widget", threshold=2.0)
        assert result["detected"] is True

    def test_execute(self):
        ta = TemporalArbitrageEngine()
        for p in [1.0, 10.0]:
            ta.record_price("item", p)
        ta.detect("item", threshold=5.0)
        result = ta.execute(0)
        assert result["executed"] is True

    def test_status(self):
        ta = TemporalArbitrageEngine()
        s = ta.status()
        assert s["total_profit"] == 0.0


class TestSponsoredExperiments:
    def test_sponsor_and_conclude(self):
        se = SponsoredExperimentsEngine()
        exp = se.sponsor("Quantum Garden", "CorpA", 100.0)
        result = se.conclude(exp.id, True, returns=250.0)
        assert result["success"] is True
        assert se.roi() > 0

    def test_status(self):
        se = SponsoredExperimentsEngine()
        se.sponsor("E1", "S1", 50.0)
        s = se.status()
        assert s["total_experiments"] == 1


class TestSimulationAsService:
    def test_purchase_and_run(self):
        saas = SimulationAsService(price_per_run=2.0)
        saas.purchase("client1", 10.0)
        result = saas.run_simulation("client1", "stress_test", {"load": 100})
        assert "result" in result
        assert result["remaining_credits"] == 8.0

    def test_insufficient_credits(self):
        saas = SimulationAsService()
        result = saas.run_simulation("broke_client", "test")
        assert "error" in result

    def test_status(self):
        saas = SimulationAsService()
        saas.purchase("c1", 5.0)
        saas.run_simulation("c1", "test")
        s = saas.status()
        assert s["total_runs"] == 1
