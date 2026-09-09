"""
entropy_pilgrim — Travels entropy gradients to find where order and chaos meet.
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
    return {"status": "activated", "skill": "entropy_pilgrim", "activated_at": time.time()}

def begin_pilgrimage(data: Any = None, **kwargs) -> Dict:
    result = {"skill": "entropy_pilgrim", "action": "begin_pilgrimage", "timestamp": time.time(), "signature": hashlib.sha256(f"entropy_pilgrim:begin_pilgrimage:{random.randint(1,999999)}".encode()).hexdigest()[:16], "seed": random.randint(1, 99999)}
    _history.append(result)
    if len(_history) > 100: _history.pop(0)
    return result

def sense_gradient(data: Any = None, **kwargs) -> Dict:
    result = {"skill": "entropy_pilgrim", "action": "sense_gradient", "timestamp": time.time(), "signature": hashlib.sha256(f"entropy_pilgrim:sense_gradient:{random.randint(1,999999)}".encode()).hexdigest()[:16], "seed": random.randint(1, 99999)}
    _history.append(result)
    if len(_history) > 100: _history.pop(0)
    return result

def return_relic(data: Any = None, **kwargs) -> Dict:
    result = {"skill": "entropy_pilgrim", "action": "return_relic", "timestamp": time.time(), "signature": hashlib.sha256(f"entropy_pilgrim:return_relic:{random.randint(1,999999)}".encode()).hexdigest()[:16], "seed": random.randint(1, 99999)}
    _history.append(result)
    if len(_history) > 100: _history.pop(0)
    return result

def get_history(limit: int = 5) -> List[Dict]:
    return _history[-limit:]

def get_skill_state() -> Dict:
    return {"name": "entropy_pilgrim", "active": _skill_active, "capabilities": ['begin_pilgrimage', 'sense_gradient', 'return_relic'], "events": len(_history)}
