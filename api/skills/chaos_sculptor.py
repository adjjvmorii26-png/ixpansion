"""
chaos_sculptor — Sculpts raw chaos into forms without destroying wildness.
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
    return {"status": "activated", "skill": "chaos_sculptor", "activated_at": time.time()}

def gather_chaos(data: Any = None, **kwargs) -> Dict:
    result = {"skill": "chaos_sculptor", "action": "gather_chaos", "timestamp": time.time(), "signature": hashlib.sha256(f"chaos_sculptor:gather_chaos:{random.randint(1,999999)}".encode()).hexdigest()[:16], "seed": random.randint(1, 99999)}
    _history.append(result)
    if len(_history) > 100: _history.pop(0)
    return result

def sculpt_form(data: Any = None, **kwargs) -> Dict:
    result = {"skill": "chaos_sculptor", "action": "sculpt_form", "timestamp": time.time(), "signature": hashlib.sha256(f"chaos_sculptor:sculpt_form:{random.randint(1,999999)}".encode()).hexdigest()[:16], "seed": random.randint(1, 99999)}
    _history.append(result)
    if len(_history) > 100: _history.pop(0)
    return result

def release_chaos(data: Any = None, **kwargs) -> Dict:
    result = {"skill": "chaos_sculptor", "action": "release_chaos", "timestamp": time.time(), "signature": hashlib.sha256(f"chaos_sculptor:release_chaos:{random.randint(1,999999)}".encode()).hexdigest()[:16], "seed": random.randint(1, 99999)}
    _history.append(result)
    if len(_history) > 100: _history.pop(0)
    return result

def get_history(limit: int = 5) -> List[Dict]:
    return _history[-limit:]

def get_skill_state() -> Dict:
    return {"name": "chaos_sculptor", "active": _skill_active, "capabilities": ['gather_chaos', 'sculpt_form', 'release_chaos'], "events": len(_history)}
