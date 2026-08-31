#!/usr/bin/env python3
"""Naturalist Walk — a single traverse through the Wave 190 observatory.

Walks the thirteen naturalist organs in the order a field naturalist would
move through a landscape: first find the lay of the land (strata), then the
hidden water (dowsing), then who holds the web together (keystone), then the
pressure from outside (solar wind), and finally the quiet places (silence).
Prints a short naturalist's field note for each.

Usage:
    python3 lab/naturalist_walk.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))
sys.path.insert(0, str(ROOT / "lab"))

from api import (antikythera_engine, bioluminescent_depth, coral_atoll,
                 dowsing_rod, heterarchy_oracle, keystone_auditor,
                 morphic_dial, osmotic_exchange, permafrost_vault,
                 plankton_bloom, silence_orchard, solar_wind_pressure,
                 stratigraphy_core)

ROUTE = [
    ("Stratigraphy Core", stratigraphy_core, "the lay of the land"),
    ("Dowsing Rod", dowsing_rod, "the hidden water"),
    ("Keystone Auditor", keystone_auditor, "who holds the web together"),
    ("Solar Wind Pressure", solar_wind_pressure, "the pressure from outside"),
    ("Silence Orchard", silence_orchard, "the quiet places"),
    ("Morphic Dial", morphic_dial, "what the ecosystem remembers"),
    ("Antikythera Engine", antikythera_engine, "the next eclipse"),
    ("Bioluminescent Depth", bioluminescent_depth, "the light in the dark"),
    ("Plankton Bloom", plankton_bloom, "the invisible micro-layer"),
    ("Coral Atoll", coral_atoll, "the accreted reefs"),
    ("Osmotic Exchange", osmotic_exchange, "the tides between families"),
    ("Permafrost Vault", permafrost_vault, "the frozen foundations"),
    ("Heterarchy Oracle", heterarchy_oracle, "the distributed will"),
]


def note(name: str, reading: dict) -> str:
    """Render a one-line field note from a reading."""
    if "deepest_stratum" in reading:
        return f"deepest stratum: {reading['deepest_stratum']}, fossils: {reading['fossil_count']}"
    if "strongest_streams" in reading:
        return f"{reading['modules_surveyed']} organs surveyed, {reading['underground_streams']} hidden streams"
    if "keystones" in reading:
        return f"base connectivity {reading['baseline_connectivity']}, {reading['keystone_count']} keystones"
    if "heliosphere_health" in reading:
        return f"boundary health {reading['heliosphere_health']}, pressure {reading['solar_wind_pressure']}"
    if "ripe_seeds" in reading:
        return f"{reading['silent']} silent beds, {len(reading['ripe_seeds'])} ripe"
    if "resonant_cluster" in reading:
        return f"field strength {reading['field_strength']}"
    if "next_eclipse_in_hours" in reading:
        return f"next eclipse in {reading['next_eclipse_in_hours']}h"
    if "gears" in reading:
        return f"{len(reading['gears'])} gears meshed"
    if "living_glowing" in reading:
        s = reading["strata"]
        return f"surface {s['surface']}, shallow {s['shallow']}, abyssal {s['abyssal']}"
    if "micro_layer_total" in reading:
        return f"micro-layer: {reading['micro_layer_total']} organisms"
    if "accretion_total" in reading:
        return f"accreted mass {reading['accretion_total']}"
    if "predicted_flows" in reading:
        return f"{reading['family_count']} families, flows predicted"
    if "permafrost_count" in reading:
        return f"{reading['permafrost_count']} frozen, {reading['thawing_count']} thawing"
    if "leaders" in reading:
        return f"leading: {reading['leaders'][0]['module']}"
    return "reading taken"


def main() -> None:
    print("✦ ——— NATURALIST WALK · Wave 190 ——— ✦\n")
    started = time.time()
    for name, organ, habitat in ROUTE:
        t0 = time.time()
        try:
            reading = organ.handler({})
            line = note(name, reading)
            print(f"  {name:<22} {habitat:<32} [{line}]  ({time.time()-t0:.2f}s)")
        except Exception as e:
            print(f"  {name:<22} {habitat:<32} [error: {e}]")
    print(f"\nfield walk complete in {time.time()-started:.1f}s")


if __name__ == "__main__":
    main()
