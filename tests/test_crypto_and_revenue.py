from __future__ import annotations
"""Tests for Crypto Payments, Credits, Referrals, Data Licensing, Governance."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def test_crypto_create_invoice():
    from api.crypto import CryptoPaymentGateway
    gw = CryptoPaymentGateway()
    inv = gw.create_invoice(29.00, "BTC", payer="test_user")
    assert inv["amount_usd"] == 29.00
    assert inv["currency"] == "BTC"
    assert inv["amount_crypto"] > 0
    assert inv["deposit_address"].startswith("bc1q")

def test_crypto_eth_invoice():
    from api.crypto import CryptoPaymentGateway
    gw = CryptoPaymentGateway()
    inv = gw.create_invoice(100.00, "ETH", payer="eth_user")
    assert inv["deposit_address"].startswith("0x")
    assert inv["amount_crypto"] > 0

def test_crypto_stablecoin():
    from api.crypto import CryptoPaymentGateway
    gw = CryptoPaymentGateway()
    inv = gw.create_invoice(50.00, "USDC")
    assert inv["amount_crypto"] == 50.0

def test_crypto_confirmation():
    from api.crypto import CryptoPaymentGateway
    gw = CryptoPaymentGateway()
    inv = gw.create_invoice(29.00, "BTC")
    for _ in range(5):
        status = gw.simulate_confirmation(inv["invoice_id"])
        if status.get("status") == "confirmed":
            break
    assert status["status"] == "confirmed"

def test_crypto_rates():
    from api.crypto import CryptoPaymentGateway
    gw = CryptoPaymentGateway()
    rates = gw.get_rates()
    assert "BTC" in rates["rates"]
    assert rates["rates"]["BTC"] > 0

def test_credits_buy():
    from api.credits import CreditSystem
    cs = CreditSystem()
    result = cs.buy_credits("user1", "explorer")
    assert result["purchased"]
    assert result["credits_added"] == 550

def test_credits_spend():
    from api.credits import CreditSystem
    cs = CreditSystem()
    cs.buy_credits("user1", "starter")
    result = cs.spend_for_experiment("user1", "quantum_tunneling")
    assert result["success"]
    assert result["spent"] == 5

def test_credits_insufficient():
    from api.credits import CreditSystem
    cs = CreditSystem()
    result = cs.spend("broke_user", 100, "test")
    assert not result["success"]

def test_credits_pricing():
    from api.credits import CreditSystem
    cs = CreditSystem()
    pricing = cs.get_pricing()
    assert "packages" in pricing
    assert "experiment_costs" in pricing

def test_referral_generate():
    from api.referral import ReferralSystem
    rs = ReferralSystem()
    result = rs.generate_code("user_a")
    assert "code" in result
    assert len(result["code"]) == 8

def test_referral_apply():
    from api.referral import ReferralSystem
    rs = ReferralSystem()
    r1 = rs.generate_code("user_a")
    result = rs.apply_code("user_b", r1["code"])
    assert result["applied"]
    stats = rs.get_stats("user_a")
    assert stats["total_referrals"] >= 1

def test_referral_leaderboard():
    from api.referral import ReferralSystem
    rs = ReferralSystem()
    r1 = rs.generate_code("alpha_lb")
    rs.apply_code("beta_lb", r1["code"])
    board = rs.leaderboard()
    assert len(board) >= 1

def test_data_licensing_browse():
    from api.data_licensing import DataLicensing
    dl = DataLicensing()
    catalog = dl.browse()
    assert len(catalog) > 0
    quantum = dl.browse(category="quantum")
    assert len(quantum) >= 1

def test_data_licensing_purchase():
    from api.data_licensing import DataLicensing
    dl = DataLicensing()
    result = dl.purchase("quantum_superposition_states", "buyer1")
    assert result["licensed"]
    access = dl.get_access(result["license_id"])
    assert access["access_granted"]

def test_data_licensing_plans():
    from api.data_licensing import DataLicensing
    dl = DataLicensing()
    plans = dl.subscription_plans()
    assert "monthly_all_access" in plans
    assert plans["monthly_all_access"]["price_usd"] == 99

def test_governance_mint():
    from api.governance import GovernanceSystem
    gov = GovernanceSystem()
    result = gov.mint("user1", "experiment_run")
    assert result["minted"] == 5
    assert result["balance"] >= 5

def test_governance_propose():
    from api.governance import GovernanceSystem
    gov = GovernanceSystem()
    gov.mint("proposer", "marketplace_sale", 200)
    result = gov.propose("New feature", "Add something cool", "proposer")
    assert result["proposed"]

def test_governance_vote():
    from api.governance import GovernanceSystem
    gov = GovernanceSystem()
    gov.mint("voter1", "test_contribution", 150)
    gov.mint("voter2", "referral", 100)
    prop = gov.propose("Test proposal", "Test", "voter1")
    v1 = gov.vote(prop["id"], "voter1", 1)
    assert v1["voted"]
    v2 = gov.vote(prop["id"], "voter2", -1)
    assert v2["voted"]

def test_governance_tokenomics():
    from api.governance import GovernanceSystem
    gov = GovernanceSystem()
    gov.mint("a", "api_call", 10)
    gov.mint("b", "api_call", 20)
    tok = gov.tokenomics()
    assert tok["total_supply"] >= 30
    assert tok["holders"] >= 2

def test_crypto_invalid_currency():
    from api.crypto import CryptoPaymentGateway
    gw = CryptoPaymentGateway()
    result = gw.create_invoice(10, "DOGE")
    assert "error" in result
