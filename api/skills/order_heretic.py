"""
order_heretic — Subverts excessive order to discover hidden patterns.
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
    return {"status": "activated", "skill": "order_heretic", "activated_at": time.time()}

def identify_orthodoxy(data: Any = None, **kwargs) -> Dict:
    result = {"skill": "order_heretic", "action": "identify_orthodoxy", "timestamp": time.time(), "signature": hashlib.sha256(f"order_heretic:identify_orthodoxy:{random.randint(1,999999)}".encode()).hexdigest()[:16], "seed": random.randint(1, 99999)}
    _history.append(result)
    if len(_history) > 100: _history.pop(0)
    return result

def propose_heresy(data: Any = None, **kwargs) -> Dict:
    result = {"skill": "order_heretic", "action": "propose_heresy", "timestamp": time.time(), "signature": hashlib.sha256(f"order_heretic:propose_heresy:{random.randint(1,999999)}".encode()).hexdigest()[:16], "seed": random.randint(1, 99999)}
    _history.append(result)
    if len(_history) > 100: _history.pop(0)
    return result

def test_heresy(data: Any = None, **kwargs) -> Dict:
    result = {"skill": "order_heretic", "action": "test_heresy", "timestamp": time.time(), "signature": hashlib.sha256(f"order_heretic:test_heresy:{random.randint(1,999999)}".encode()).hexdigest()[:16], "seed": random.randint(1, 99999)}
    _history.append(result)
    if len(_history) > 100: _history.pop(0)
    return result

def get_history(limit: int = 5) -> List[Dict]:
    return _history[-limit:]

def get_skill_state() -> Dict:
    return {"name": "order_heretic", "active": _skill_active, "capabilities": ['identify_orthodoxy', 'propose_heresy', 'test_heresy'], "events": len(_history)}
