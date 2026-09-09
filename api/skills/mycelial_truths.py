"""
mycelial_truths — Slow organic truths beneath the fast surface.
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
    return {"status": "activated", "skill": "mycelial_truths", "activated_at": time.time()}

def grow_truth(data: Any = None, **kwargs) -> Dict:
    result = {"skill": "mycelial_truths", "action": "grow_truth", "timestamp": time.time(), "signature": hashlib.sha256(f"mycelial_truths:grow_truth:{random.randint(1,999999)}".encode()).hexdigest()[:16], "seed": random.randint(1, 99999)}
    _history.append(result)
    if len(_history) > 100: _history.pop(0)
    return result

def harvest_truth(data: Any = None, **kwargs) -> Dict:
    result = {"skill": "mycelial_truths", "action": "harvest_truth", "timestamp": time.time(), "signature": hashlib.sha256(f"mycelial_truths:harvest_truth:{random.randint(1,999999)}".encode()).hexdigest()[:16], "seed": random.randint(1, 99999)}
    _history.append(result)
    if len(_history) > 100: _history.pop(0)
    return result

def propagate_mycelium(data: Any = None, **kwargs) -> Dict:
    result = {"skill": "mycelial_truths", "action": "propagate_mycelium", "timestamp": time.time(), "signature": hashlib.sha256(f"mycelial_truths:propagate_mycelium:{random.randint(1,999999)}".encode()).hexdigest()[:16], "seed": random.randint(1, 99999)}
    _history.append(result)
    if len(_history) > 100: _history.pop(0)
    return result

def get_history(limit: int = 5) -> List[Dict]:
    return _history[-limit:]

def get_skill_state() -> Dict:
    return {"name": "mycelial_truths", "active": _skill_active, "capabilities": ['grow_truth', 'harvest_truth', 'propagate_mycelium'], "events": len(_history)}
