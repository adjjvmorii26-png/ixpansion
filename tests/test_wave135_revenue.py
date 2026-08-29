"""Wave 135 — Revenue Orchestration Layer tests."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))

from revenue_orchestrator import RevenueOrchestrator
from tiered_access_system import TieredAccessSystem, PLANS
from service_sla import ServiceSLA
from royalty_registry import RoyaltyRegistry
from marketplace_fees import MarketplaceFees
from client_portal import ClientPortal
from invoice_engine import InvoiceEngine
from growth_engine import GrowthEngine


def test_wave135_revenue_orchestrator():
    ro = RevenueOrchestrator()
    ro.register("marketplace fees", "transaction", rate=10.0)
    ro.register("subscriptions", "recurring", rate=50.0)
    total = ro.collect_cycle(multiplier=1.0)
    assert total == 60.0
    assert ro.projected_annualized() > 0
    assert ro.status()["streams"] >= 2


def test_wave135_tiered_access_system():
    tas = TieredAccessSystem()
    sub = tas.subscribe("acme", "pro")
    assert sub.quota() == PLANS["pro"]["quota"]
    assert tas.charge_usage(sub.id, 10)
    assert not tas.charge_usage(sub.id, 1000)  # exceeds quota
    assert tas.upgrade(sub.id, "nexus")
    assert tas.monthly_recurring() == 99.0
    assert tas.status()["subscribers"] >= 1


def test_wave135_service_sla():
    sla = ServiceSLA()
    order = sla.book("acme", "dialect build", target_hours=24.0)
    assert sla.deliver(order.id, hours_taken=20.0)  # on time
    order2 = sla.book("acme", "late build", target_hours=10.0)
    assert sla.deliver(order2.id, hours_taken=30.0)  # late
    assert order2.credit > 0
    assert sla.status()["on_time_rate"] < 1.0
    assert sla.status()["issued_credits"] > 0


def test_wave135_royalty_registry():
    rr = RoyaltyRegistry()
    asset = rr.register("fractal blueprint", ["alice", "bob"])
    payouts = rr.resale(asset.id, 1000.0, share=0.05)
    assert abs(sum(payouts.values()) - 50.0) < 0.01
    assert rr.balance("alice") == 25.0
    assert rr.status()["royalties_paid"] > 0


def test_wave135_marketplace_fees():
    mf = MarketplaceFees(fee_rate=0.05, treasury_share=0.4)
    result = mf.assess(1000.0)
    assert result["fee"] == 50.0
    assert mf.treasury_balance() == 20.0
    assert mf.worker_fund_balance() == 30.0
    assert mf.status()["transactions"] >= 1


def test_wave135_client_portal():
    cp = ClientPortal()
    client = cp.onboard("acme", plan="pro")
    assert cp.deliver(client.id, "report v1")
    ticket = cp.support(client.id, "agent bug")
    assert ticket
    assert cp.suspend(client.id)
    assert cp.status()["clients"] >= 1
    assert cp.status()["total_deliverables"] >= 1


def test_wave135_invoice_engine():
    ie = InvoiceEngine()
    inv = ie.create("acme", {"design": 500.0, "deploy": 300.0}, issue=True)
    assert inv.status == "issued"
    assert ie.pay(inv.id, 800.0)
    assert inv.status == "paid"
    inv2 = ie.create("beta", {"design": 100.0}, issue=True)
    assert ie.escalate(inv2.id)
    assert ie.status()["collected"] == 800.0
    assert ie.status()["overdue"] >= 1


def test_wave135_growth_engine():
    ge = GrowthEngine(treasury=1000.0)
    inv = ge.propose("new guild", capital=200.0, projected_roi=1.5)
    assert ge.fund(inv.id)
    assert ge.treasury == 800.0
    assert ge.realize(inv.id, actual_return=350.0)
    assert ge.treasury == 1150.0
    assert ge.status()["realized_return"] == 350.0


def test_wave135_handlers():
    from revenue_orchestrator import handler as h1
    from tiered_access_system import handler as h2
    from service_sla import handler as h3
    from royalty_registry import handler as h4
    from marketplace_fees import handler as h5
    from client_portal import handler as h6
    from invoice_engine import handler as h7
    from growth_engine import handler as h8
    for h in (h1, h2, h3, h4, h5, h6, h7, h8):
        r = h({})
        assert r["status"] == "active"
