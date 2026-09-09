"""
signal_whisperer — Listens to weak signals most systems ignore.
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
    return {"status": "activated", "skill": "signal_whisperer", "activated_at": time.time()}

def listen(data: Any = None, **kwargs) -> Dict:
    result = {"skill": "signal_whisperer", "action": "listen", "timestamp": time.time(), "signature": hashlib.sha256(f"signal_whisperer:listen:{random.randint(1,999999)}".encode()).hexdigest()[:16], "seed": random.randint(1, 99999)}
    _history.append(result)
    if len(_history) > 100: _history.pop(0)
    return result

def extract_signal(data: Any = None, **kwargs) -> Dict:
    result = {"skill": "signal_whisperer", "action": "extract_signal", "timestamp": time.time(), "signature": hashlib.sha256(f"signal_whisperer:extract_signal:{random.randint(1,999999)}".encode()).hexdigest()[:16], "seed": random.randint(1, 99999)}
    _history.append(result)
    if len(_history) > 100: _history.pop(0)
    return result

def amplify_weak(data: Any = None, **kwargs) -> Dict:
    result = {"skill": "signal_whisperer", "action": "amplify_weak", "timestamp": time.time(), "signature": hashlib.sha256(f"signal_whisperer:amplify_weak:{random.randint(1,999999)}".encode()).hexdigest()[:16], "seed": random.randint(1, 99999)}
    _history.append(result)
    if len(_history) > 100: _history.pop(0)
    return result

def get_history(limit: int = 5) -> List[Dict]:
    return _history[-limit:]

def get_skill_state() -> Dict:
    return {"name": "signal_whisperer", "active": _skill_active, "capabilities": ['listen', 'extract_signal', 'amplify_weak'], "events": len(_history)}
