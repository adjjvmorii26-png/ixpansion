#!/usr/bin/env python3
"""Repair Guild — one ceremony for the six kintsugi organs.

Walks the repair lineage the way a guild would conduct a restoration:
map the cracks, listen for strain, forge the seams, account the debt,
honor the vessels on the altar, and perform the ritual that binds them.

Usage:
    python3 lab/repair_guild.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

from api import (crack_mapper, crack_seams, fracture_listener,
                 kintsugi_altar, kintsugi_debt_ledger, repair_ritual)

ORDER = [
    ("Crack Mapper", crack_mapper, "the cartography of damage"),
    ("Fracture Listener", fracture_listener, "hearing strain before the break"),
    ("Crack Seams", crack_seams, "forging golden seams"),
    ("Kintsugi Debt Ledger", kintsugi_debt_ledger, "accounting fragility vs gold"),
    ("Kintsugi Altar", kintsugi_altar, "honoring the repaired vessels"),
]


def main() -> None:
    print("⚒ ——— REPAIR GUILD · Wave 191 ——— ⚒\n")
    total_cracks = 0
    total_seams = 0
    t0 = time.time()
    for name, organ, role in ORDER:
        s = time.time()
        reading = organ.handler({})
        if name == "Crack Mapper":
            total_cracks = reading.get("crack_count", 0)
            line = f"{total_cracks} cracks mapped"
        elif name == "Crack Seams":
            total_seams = reading.get("seam_count", 0)
            line = f"{total_seams} golden seams"
        elif name == "Kintsugi Debt Ledger":
            line = f"net {reading.get('net_balance')} ({reading.get('repayment_status')})"
        elif name == "Kintsugi Altar":
            line = f"{reading.get('honored_vessels')} vessels honored"
        else:
            line = f"{reading.get('strains_heard', 0)} strains heard"
        print(f"  {name:<24} {role:<36} [{line}]  ({time.time()-s:.2f}s)")
    print("\n  ——— performing the ritual ———")
    ritual = repair_ritual.perform()
    print(f"  ceremony complete in {ritual.get('duration_s')}s · "
          f"{ritual.get('cracks_named')} cracks, {ritual.get('seams_total')} seams, "
          f"{ritual.get('vessels_honored')} vessels honored")
    print(f"\n  {ritual.get('koan')}")
    print(f"\n  total guild walk: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
