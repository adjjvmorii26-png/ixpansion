"""Stream Reactor API — server-sent events style reactor for live updates."""
from __future__ import annotations
import json
import sys
import hashlib
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def generate_reactor_stream():
    """Generate a snapshot of reactor state (SSE-compatible JSON envelope)."""
    # Collect reactor signals from all experimental modules
    lab_dir = ROOT / "lab" / "experiments"
    signals = []

    if lab_dir.exists():
        for py in sorted(lab_dir.glob("*.py"))[:20]:
            if py.name.startswith("_"):
                continue
            text = py.read_text(errors="replace")
            # Extract a hash of the module's current state
            sig = hashlib.md5(text.encode()).hexdigest()[:8]
            signals.append({
                "module": py.stem,
                "hash": sig,
                "lines": len(text.splitlines()),
            })

    # Build a composite pulse signal
    composite_hash = hashlib.sha256(
        "".join(s["hash"] for s in signals).encode()
    ).hexdigest()[:16]

    # Energy level based on module count and size
    total_lines = sum(s["lines"] for s in signals)
    energy = min(1.0, total_lines / 50000.0)

    # Entropy from hash distribution
    entropy = len(set(s["hash"] for s in signals)) / max(1, len(signals))

    return {
        "event": "reactor_pulse",
        "timestamp": int(time.time()),
        "pulse": {
            "composite_hash": composite_hash,
            "energy": round(energy, 4),
            "entropy": round(entropy, 4),
            "module_count": len(signals),
            "total_lines": total_lines,
        },
        "signals": signals[:20],
        "note": "This is a single-pulse snapshot. For streaming, connect via WebSocket.",
    }


def handler(request, response):
    if hasattr(response, "headers"):
        response.headers["Content-Type"] = "text/event-stream"
        response.headers["Cache-Control"] = "no-cache"
    return generate_reactor_stream()


if __name__ == "__main__":
    print(json.dumps(handler(None, None), indent=2))


def coherence_vitals() -> dict:
    """Stream Reactor reports — live event flow."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "reactor_vitality": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
    }

def resonates_with() -> list:
    """Declared kinships."""
    return ['event_stream', 'frontier_stream']
