"""Specialized substrates 737–742."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

import wave737_paradox_debt_ledger as w737
import wave738_oblivion_compost as w738
import wave739_receipt_notary as w739
import wave740_negotiation_bazaar as w740
import wave741_dialect_mutator as w741
import wave742_actuator_bridge as w742


def test_737_debt():
    assert w737.coherence_vitals()["wave"] == 737
    r = w737.handler({"action": "incur", "paradox": "A and not A", "principal": 1.5})
    assert r["status"] == "incurred"
    assert "allowed" in w737.handler({"action": "can_spend", "amount": 0})


def test_738_compost():
    assert w738.handler({"action": "compost", "module": "wave_test_dead", "nutrient": 2})["status"] == "composted"
    assert w738.handler({"action": "draw", "amount": 1})["status"] == "drawn"


def test_739_notary():
    r = w739.handler({"action": "issue", "kind": "test", "body": {"x": 1}})
    assert r["status"] == "issued" and r["receipt"]["sig"]


def test_740_bazaar():
    w740.handler({"action": "bid", "kind": "attention", "price": 2, "agent": "a"})
    w740.handler({"action": "ask", "kind": "attention", "price": 1, "agent": "b"})
    assert w740.handler({"action": "clear"})["status"] == "cleared"


def test_741_dialect():
    assert w741.handler({"action": "mutate", "seed": "fixed"})["status"] == "mutated"


def test_742_actuator():
    assert w742.handler({"action": "act", "effector": "log", "payload": {"n": 1}, "dry_run": True})["status"] == "acted"
