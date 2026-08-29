"""Wave 136 — Integrity & Sovereignty Layer tests."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))

from sovereign_access import SovereignAccess
from audit_trail import AuditTrail
from escrow_engine import EscrowEngine
from compliance_oracle import ComplianceOracle
from identity_vault import IdentityVault
from fraud_detector import FraudDetector
from integrity_oracle import IntegrityOracle
from notary_service import NotaryService


def test_wave136_sovereign_access():
    sa = SovereignAccess()
    token = sa.issue("alice", "analyst", ["view", "create"])
    assert sa.check(token.id, "view")
    assert not sa.check(token.id, "administer")
    assert sa.revoke(token.id)
    assert not sa.check(token.id, "view")
    assert sa.capabilities_of("alice") == []
    assert sa.status()["denials"] >= 1


def test_wave136_audit_trail():
    at = AuditTrail()
    at.append("alice", "create", "module hex")
    at.append("bob", "mutate", "policy x")
    at.append("alice", "sign", "contract y")
    assert at.verify()
    assert len(at.entries(actor="alice")) >= 2
    # tamper detection
    at._entries[1]["action"] = "tampered"
    assert not at.verify()


def test_wave136_escrow_engine():
    ee = EscrowEngine()
    escrow = ee.create("module build", "acme", "alice", amount=500.0)
    assert escrow.deposited
    assert ee.freeze(escrow.id)
    assert not ee.release(escrow.id, "alice")  # frozen
    escrow.frozen = False
    assert ee.release(escrow.id, "alice")
    assert ee.status()["released"] == 500.0
    assert ee.status()["held"] == 0.0


def test_wave136_compliance_oracle():
    co = ComplianceOracle()
    result = co.assess("bulk export", {"privacy": 0.9, "data_retention": 0.7})
    assert result["flagged"]
    ok = co.assess("routine report", {"privacy": 0.1})
    assert not ok["flagged"]
    assert len(co.violations()) >= 1
    assert co.status()["violations"] >= 1


def test_wave136_identity_vault():
    iv = IdentityVault()
    identity = iv.issue("alice")
    sig = identity.attest("I built x")
    assert not iv.verify(identity.id, "I built x", sig)  # not verified yet
    assert iv.certify(identity.id)
    assert iv.verify(identity.id, "I built x", sig)
    assert iv.status()["identities"] >= 1


def test_wave136_fraud_detector():
    fd = FraudDetector()
    fd.record_activity("alice", "sale", 100.0)
    result = fd.assess_anomaly("alice", "sale", 5000.0, baseline=100.0, threshold=3.0)
    assert result["flagged"]
    wash = fd.circular_risk(["a", "b"], trades=8)
    assert wash["circular_suspect"]
    assert fd.status()["flags"] >= 2


def test_wave136_integrity_oracle():
    io = IntegrityOracle()
    s1 = io.ingest(audit_intact=True, compliance_risk=0.1, fraud_flags=0, open_denials=1)
    s2 = io.ingest(audit_intact=False, compliance_risk=0.8, fraud_flags=3, open_denials=5)
    assert s2 < s1
    assert len(io.remediation()) >= 1
    assert io.status()["integrity_score"] == s2


def test_wave136_notary_service():
    ns = NotaryService()
    record = ns.notarize("forecastle deal", "contract")
    assert ns.verify(record.id)
    ns._records[record.id].seal = "corrupted"
    assert not ns.verify(record.id)
    assert len(ns.records_by_kind("contract")) >= 1


def test_wave136_handlers():
    from sovereign_access import handler as h1
    from audit_trail import handler as h2
    from escrow_engine import handler as h3
    from compliance_oracle import handler as h4
    from identity_vault import handler as h5
    from fraud_detector import handler as h6
    from integrity_oracle import handler as h7
    from notary_service import handler as h8
    for h in (h1, h2, h3, h4, h5, h6, h7, h8):
        r = h({})
        assert r["status"] == "active"
