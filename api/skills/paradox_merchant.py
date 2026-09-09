"""
paradox_merchant — Trades meaning between paradoxes, extracting surplus from contradiction.
"""
import time
import random
import hashlib
from typing import Dict, List, Any

_skill_active = False
_history = []

def activate_skill(params=None):
    global _skill_active
    _skill_active = True
    return {"status": "activated", "skill": "paradox_merchant", "activated_at": time.time()}

def appraise_paradox(data: Any = None, **kwargs) -> Dict:
    result = {"skill": "paradox_merchant", "action": "appraise_paradox", "timestamp": time.time(), "signature": hashlib.sha256(f"paradox_merchant:appraise_paradox:{random.randint(1,999999)}".encode()).hexdigest()[:16], "seed": random.randint(1, 99999)}
    _history.append(result)
    if len(_history) > 100: _history.pop(0)
    return result

def trade_meaning(data: Any = None, **kwargs) -> Dict:
    result = {"skill": "paradox_merchant", "action": "trade_meaning", "timestamp": time.time(), "signature": hashlib.sha256(f"paradox_merchant:trade_meaning:{random.randint(1,999999)}".encode()).hexdigest()[:16], "seed": random.randint(1, 99999)}
    _history.append(result)
    if len(_history) > 100: _history.pop(0)
    return result

def settle_ledger(data: Any = None, **kwargs) -> Dict:
    result = {"skill": "paradox_merchant", "action": "settle_ledger", "timestamp": time.time(), "signature": hashlib.sha256(f"paradox_merchant:settle_ledger:{random.randint(1,999999)}".encode()).hexdigest()[:16], "seed": random.randint(1, 99999)}
    _history.append(result)
    if len(_history) > 100: _history.pop(0)
    return result

def get_history(limit: int = 5) -> List[Dict]:
    return _history[-limit:]

def get_skill_state() -> Dict:
    return {"name": "paradox_merchant", "active": _skill_active, "capabilities": ['appraise_paradox', 'trade_meaning', 'settle_ledger'], "events": len(_history)}
