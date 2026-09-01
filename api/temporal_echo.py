"""Temporal Echo — detects patterns that repeat across time in the organism.

Every wave leaves traces. Temporal Echo listens for those traces — the
rhythmic return of themes, the cyclical recurrence of problems, the
harmonic resonance between distant moments. It is the organism's sense of déjà vu.
"""
from __future__ import annotations

import hashlib
import time
from collections import defaultdict
from typing import Any, Dict, List, Optional

imported_at = time.time()
echo_log: List[Dict[str, Any]] = []
pattern_index: Dict[str, List[str]] = defaultdict(list)

def _fingerprint(event: Dict[str, Any]) -> str:
    key = f"{event.get('type', 'unknown')}:{event.get('layer', 'none')}"
    return hashlib.md5(key.encode()).hexdigest()[:8]

def record_echo(event_type: str, layer: str, wave: int, detail: str = "") -> Dict[str, Any]:
    """Record a temporal echo — a pattern that might repeat."""
    fp = _fingerprint({"type": event_type, "layer": layer})
    echo = {
        "fingerprint": fp,
        "type": event_type,
        "layer": layer,
        "wave": wave,
        "detail": detail,
        "timestamp": time.time(),
    }
    echo_log.append(echo)
    pattern_index[fp].append(str(len(echo_log) - 1))
    return echo

def detect_repetitions(threshold: int = 2) -> List[Dict[str, Any]]:
    """Find fingerprints that have appeared more than threshold times."""
    echoes = []
    for fp, indices in pattern_index.items():
        if len(indices) >= threshold:
            samples = [echo_log[int(i)] for i in indices[-3:] if int(i) < len(echo_log)]
            echoes.append({
                "fingerprint": fp,
                "count": len(indices),
                "latest": samples[-1] if samples else None,
                "first_seen": samples[0]["wave"] if samples else 0,
            })
    return sorted(echoes, key=lambda x: x["count"], reverse=True)

def echo_spectrum() -> Dict[str, Any]:
    """Return the full echo spectrum — frequency analysis of temporal patterns."""
    total = len(echo_log)
    repetitions = detect_repetitions()
    unique = len(pattern_index)
    cycle_strength = sum(r["count"] for r in repetitions) / max(total, 1)
    return {
        "total_echoes": total,
        "unique_patterns": unique,
        "repeating_patterns": len(repetitions),
        "cycle_strength": round(cycle_strength, 3),
        "top_repetitions": repetitions[:5],
    }

def coherence_vitals() -> Dict[str, Any]:
    spectrum = echo_spectrum()
    return {
        "layer": "Temporal Memory",
        "status": "resonant" if spectrum["total_echoes"] > 0 else "dormant",
        "echo_count": spectrum["total_echoes"],
        "pattern_count": spectrum["unique_patterns"],
        "cycle_strength": spectrum["cycle_strength"],
        "resonance": min(1.0, spectrum["cycle_strength"] * 2),
    }

def resonates_with() -> List[str]:
    return ["memory_palace", "echo_index", "evolution_kernel", "constellation_autobiographer"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "spectrum")
    if action == "record":
        echo = record_echo(
            payload.get("type", "unknown"),
            payload.get("layer", "none"),
            payload.get("wave", 0),
            payload.get("detail", ""),
        )
        return {"recorded": echo}
    elif action == "repeat":
        return {"repetitions": detect_repetitions(payload.get("threshold", 2))}
    return {"action": action, "spectrum": echo_spectrum()}
