"""Wave 448 - Debris Field Mapper

Tracks fragmentation clouds in orbital shells: parents, fragments, hotspots,
and the slow Kessler arithmetic of a sky filling with shrapnel. Maps what is
left behind when something upstairs breaks.
"""
from __future__ import annotations
import hashlib
import json
import time
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DEBRIS_LOG = Path(DATA_DIR) / "debris_field_mapper.json"

CATALOG = [
    {"parent": "COSMOS-1408", "year": 2021, "altitude_km": 485, "fragments": 1500, "mass_kg": 2200},
    {"parent": "FENGYUN-1C", "year": 2007, "altitude_km": 865, "fragments": 3400, "mass_kg": 880},
    {"parent": "IRS-1P", "year": 2019, "altitude_km": 471, "fragments": 120, "mass_kg": 960},
    {"parent": "DMSP-F13", "year": 2015, "altitude_km": 840, "fragments": 100, "mass_kg": 740},
    {"parent": "IXP-SENTINEL-1", "year": 2025, "altitude_km": 800, "fragments": 0, "mass_kg": 340},
    {"parent": "SOZ-BLOCKER", "year": 2013, "altitude_km": 1480, "fragments": 77, "mass_kg": 1350},
]

SHELLS = [(300, 400), (400, 500), (500, 600), (600, 800), (800, 1000), (1000, 1200), (1200, 1500)]


def _hash_split(text, k):
    h = int(hashlib.sha256(text.encode()).hexdigest(), 16)
    return [(h >> (i * 8)) & 0xFF for i in range(k)]


def shell_census(catalog=None):
    catalog = catalog if catalog is not None else CATALOG
    shells = []
    for lo, hi in SHELLS:
        members = [c for c in catalog if lo <= c["altitude_km"] < hi]
        fragments = sum(c["fragments"] for c in members)
        shells.append({
            "shell_km": f"{lo}-{hi}", "parents": len(members),
            "fragments": fragments, "density_tracked": round(fragments / max(1, hi - lo), 3),
        })
    return shells


def hotspots(catalog=None):
    census = shell_census(catalog)
    ranked = sorted(census, key=lambda s: -s["density_tracked"])
    return [{"rank": i + 1, **s} for i, s in enumerate(ranked)]


def breakup(parent="IXP-SENTINEL-1", altitude_km=800, mass_kg=340):
    """Simulate a fragmentation event and append the new cloud to the catalog."""
    seed_bits = _hash_split(f"{parent}:{altitude_km}:{int(time.time() // 3600)}", 4)
    n_fragments = 30 + sum(seed_bits) % 180
    v_spread = round(0.02 + (seed_bits[1] % 40) / 100.0, 3)  # km/s
    event = {
        "parent": parent, "year": time.strftime("%Y"), "altitude_km": altitude_km,
        "fragments": n_fragments, "mass_kg": mass_kg, "velocity_spread_km_s": v_spread,
        "event_ts": time.time(),
    }
    CATALOG.append(event)
    return event


def projection(years=2):
    """A crude Kessler arithmetic: cascade multiplier per shell over years."""
    census = shell_census()
    rows = []
    for s in census:
        base = s["fragments"]
        # Near-term cascade chance grows with density and resident parents.
        cascade = base * (1 + s["density_tracked"] * 0.5) ** (years * 0.25)
        rows.append({"shell_km": s["shell_km"], "fragments_today": base,
                     "fragments_after_years": int(cascade),
                     "growth_ratio": round((cascade / base) if base else 0.0, 3)})
    return rows


def handler(payload: dict = None, context: dict = None) -> dict:
    p = payload or {}
    action = str(p.get("action", "census")).lower()
    if action == "breakup":
        event = breakup(str(p.get("parent", "IXP-SENTINEL-1")),
                        float(p.get("altitude_km", 800.0)), float(p.get("mass_kg", 340.0)))
        return {"action": "debris_field_mapper", "event": event,
                "census": shell_census(), "hotspots": hotspots()[:3]}
    if action == "projection":
        return {"action": "debris_field_mapper", "projection": projection(
            years=float(p.get("years", 2.0)))}
    return {"action": "debris_field_mapper", "census": shell_census(),
            "hotspots": hotspots()[:3],
            "total_tracked_fragments": sum(s["fragments"] for s in shell_census()),
            "growth_note": "shell densities drive the cascade arithmetic"}


def coherence_vitals() -> dict:
    census = shell_census()
    return {"layer": "orbital", "status": "resonant", "resonance": 0.84, "wave": "448",
            "parents_tracked": len(CATALOG),
            "total_fragments": sum(s["fragments"] for s in census),
            "hottest_shell": hotspots()[0]["shell_km"] if hotspots() else "none"}


def resonates_with() -> list:
    return ["orbit_cohesion_field", "decay_forecaster", "extinction_mapper",
            "constellation_topology", "telemetry_anomaly_oracle", "fossil_registry"]
