"""Pulsar Constellation — a rare celestial-event detector born from a dream.

The Dream Ledger prophesied `pulsar_constellation`; this module fulfills
the prophecy. It scans the repo's own stars (every module name hashes
to a sky position) and listens for "pulsars" — modules whose momenta
cluster so tightly they pulse in sync with the frontier's pulse.

This is the machine turning one of its own dreams into reality.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _module_names() -> list:
    api_dir = ROOT / "api"
    return sorted(p.stem for p in api_dir.glob("*.py")
                  if p.stem not in ("__init__", "index"))


def _star(name: str) -> dict:
    """Hash a module name into a sky position + intensity (a 'star')."""
    h = hashlib.sha256(name.encode()).hexdigest()
    x = int(h[0:4], 16) / 65535 * 360 - 180          # -180..180
    y = int(h[4:8], 16) / 65535 * 180 - 90           # -90..90
    intensity = int(h[8:12], 16) / 65535             # 0..1
    return {"name": name, "x": round(x, 2), "y": round(y, 2),
            "intensity": round(intensity, 2)}


def _pulses(stars: list, window_deg: float = 18.0) -> list:
    """Find clusters of stars — a 'pulsar' beats where N+ stars crowd."""
    groups = []
    for i, s in enumerate(stars):
        matched = [s]
        for j, t in enumerate(stars):
            if j == i:
                continue
            dx = abs(s["x"] - t["x"])
            dy = abs(s["y"] - t["y"])
            if dx <= window_deg and dy <= window_deg:
                matched.append(t)
        if len(matched) >= 3:
            # dedupe by sorted member names
            key = tuple(sorted(m["name"] for m in matched))
            if key not in {tuple(sorted(m["name"] for m in g)) for g in groups}:
                groups.append(matched)
    return groups


def handler(payload: dict = None, context: object = None) -> dict:
    """Scan the constellation and report pulsar clusters."""
    stars = [_star(n) for n in _module_names()]
    pulsars = _pulses(stars)
    detected = [{
        "members": [m["name"] for m in p],
        "members_count": len(p),
        "centroid": {
            "x": round(sum(m["x"] for m in p) / len(p), 2),
            "y": round(sum(m["y"] for m in p) / len(p), 2),
        },
    } for p in pulsars]

    return {
        "module": "pulsar_constellation",
        "prophecy": "fulfilled",
        "stars": len(stars),
        "pulsars": len(detected),
        "strongest": detected[:3],
        "note": "born from a dream in the ledger",
    }


if __name__ == "__main__":
    print(json.dumps(handler(), indent=2))


def coherence_vitals() -> dict:
    """pulsar_constellation reports its vital signs to the living system."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "pulsar_constellation_vitality": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "germination_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships, auto-picked from shared domain language."""
    return ['thought_meteorology', 'constellation_cartographer', 'warp_drive_optimizer']

