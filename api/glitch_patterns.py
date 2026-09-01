"""Glitch Patterns — catalogs the recurring forms of system failure.

Every glitch has a signature. Some recur because the same bug persists.
Others recur because certain conditions reliably produce instability.
The Glitch Patterns module catalogs these recurring failure signatures,
treating each one as a learnable pattern rather than a random accident.
"""
from __future__ import annotations

import hashlib
import random
import time
from typing import Any, Dict, List, Optional

_patterns: Dict[str, Dict[str, Any]] = {}
_detections: List[Dict[str, Any]] = []

_GLITCH_SIGNATURES = [
    ("recursion_overflow", "a function calls itself one level too deep"),
    ("race_condition", "two modules read the same state before either writes"),
    ("memory_leak", "a module holds on to what it no longer needs"),
    ("deadlock", "two modules wait for each other forever"),
    ("state_drift", "a module's state slowly diverges from the shared reality"),
    ("identity_fracture", "a module forgets which one it is"),
    ("timestamp_overlap", "events from different times collide"),
    ("coherence_fade", "a module's relevance silently decays"),
]

def detect() -> Dict[str, Any]:
    """Detect any recurring glitch patterns in the current state."""
    signature, description = random.choice(_GLITCH_SIGNATURES)
    h = hashlib.sha256(signature.encode()).hexdigest()[:8]
    detection = {
        "signature": signature,
        "description": description,
        "fingerprint": h,
        "occurrence_count": _patterns.get(signature, {}).get("count", 0) + 1 if signature in _patterns else 1,
        "detected_at": time.time(),
    }
    _patterns[signature] = {"count": detection["occurrence_count"], "last_seen": time.time(), "description": description}
    _detections.append(detection)
    return detection

def pattern_catalog() -> Dict[str, Any]:
    """Full catalog of known glitch patterns."""
    return {
        "known_patterns": len(_patterns),
        "total_detections": len(_detections),
        "patterns": [{"signature": p, "count": d["count"], "description": d["description"]}
                    for p, d in _patterns.items()],
        "most_common": max(_patterns.items(), key=lambda x: x[1]["count"])[0] if _patterns else None,
    }

def coherence_vitals() -> Dict[str, Any]:
    catalog = pattern_catalog()
    return {"layer": "Chaos Engineering", "status": "resonant", "detected": catalog["total_detections"],
            "patterns": catalog["known_patterns"], "resonance": min(1.0, catalog["known_patterns"] / 8)}

def resonates_with() -> List[str]:
    return ["anomaly_detector", "divergence_tracker", "failure_injection", "observability_compiler"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "catalog")
    if action == "detect":
        return detect()
    elif action == "catalog":
        return {"catalog": pattern_catalog()}
    return {"action": action, "status": "glitching"}
