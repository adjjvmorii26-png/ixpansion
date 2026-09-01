"""Time Loop Detector — catches recursive patterns and temporal echoes.

Some patterns repeat not because they're good, but because the organism
is stuck. The Time Loop Detector identifies when the same sequence of
events, modules, or decisions repeats — and alerts the organism that
it's caught in a loop rather than progressing.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional

_event_buffer: List[str] = []
_loops_detected: List[Dict[str, Any]] = []

def record_event(event: str) -> None:
    """Record an event for loop detection."""
    _event_buffer.append(event)
    if len(_event_buffer) > 100:
        _event_buffer.pop(0)

def check_loops(window: int = 20) -> Dict[str, Any]:
    """Check for repeating sequences in recent events."""
    if len(_event_buffer) < 4:
        return {"loops": [], "buffer_size": len(_event_buffer)}
    
    recent = _event_buffer[-window:]
    loops = []
    
    for pattern_len in range(2, min(len(recent) // 2 + 1, 10)):
        for start in range(len(recent) - pattern_len * 2):
            pattern = recent[start:start + pattern_len]
            check = recent[start + pattern_len:start + pattern_len * 2]
            if pattern == check:
                loop = {
                    "pattern": pattern,
                    "length": pattern_len,
                    "detected_at": time.time(),
                    "severity": min(1.0, pattern_len / 5),
                }
                loops.append(loop)
                if loop not in [l for l in _loops_detected]:
                    _loops_detected.append(loop)
    
    return {"loops": loops, "buffer_size": len(_recent := recent),
            "total_loops_ever": len(_loops_detected)}

def coherence_vitals() -> Dict[str, Any]:
    result = check_loops()
    return {"layer": "Chaos Engineering", "status": "resonant" if not result["loops"] else "drifting",
            "buffer": result["buffer_size"], "loops": result["total_loops_ever"],
            "resonance": max(0.3, 1.0 - len(result["loops"]) * 0.2)}

def resonates_with() -> List[str]:
    return ["temporal_echo", "paradox_injector", "divergence_tracker", "recursion_driver"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "check")
    if action == "record":
        record_event(payload.get("event", ""))
        return {"recorded": True, "buffer": len(_event_buffer)}
    elif action == "check":
        return {"result": check_loops(payload.get("window", 20))}
    return {"action": action, "status": "watching"}
