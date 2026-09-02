#!/usr/bin/env python3
"""Wave 218 — Auto-Enact: discovers + lays new bridge stones.

Usage:
    python3 tools/auto_enact.py            # scan + enact (dry-run if no token)
    python3 tools/auto_enact.py --dry-run  # show what would be enacted
    python3 tools/auto_enact.py --force    # re-enact ALL bridges (ignore ledger)

Must run from the ixpansion repo root with API modules importable.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from api.bridge_enactor import handler as enact_handler
from api.interstice_bridge import _INTERSTICE_MAP
from api.resonance_sentinel import handler as sentinel_handler


def discover_unenacted() -> list[dict]:
    ledger_path = ROOT / "data" / "bridges" / "ledger.json"
    enacted = set()
    try:
        ledger = json.load(open(ledger_path))
        enacted = {(s["repo"], s["organ"]) for s in ledger.get("stones", [])}
    except Exception:
        pass

    bridges = _INTERSTICE_MAP.get("top_bridges", [])
    new = [b for b in bridges if (b["repo"], b["organ"]) not in enacted]
    return new


def main():
    parser = argparse.ArgumentParser(description="Auto-enact new bridge stones")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be enacted")
    parser.add_argument("--force", action="store_true", help="Re-enact ALL bridges (ignore ledger)")
    parser.add_argument("--limit", type=int, default=50, help="Max bridges to enact per run")
    args = parser.parse_args()

    token = os.environ.get("IXP_GH_TOKEN", "")
    if not token:
        try:
            token = open(ROOT / ".env").read().split("IXP_GH_TOKEN=")[1].strip()
        except Exception:
            pass
    if token:
        os.environ["IXP_GH_TOKEN"] = token

    print("=== Resonance Sentinel ===")
    s = sentinel_handler({"action": "health"})
    print(f"  health_index: {s['health_index']}")
    print(f"  drift:        {s['drift']} bridges")
    print(f"  rot:          {s['rot']} stones")
    print()

    bridges = _INTERSTICE_MAP.get("top_bridges", [])
    print(f"=== Interstice Map: {len(bridges)} bridges ===")
    print()

    if args.force:
        to_act = bridges[:args.limit]
    else:
        to_act = discover_unenacted()[:args.limit]

    print(f"=== {len(to_act)} bridges to enact ===")
    if args.dry_run:
        for b in to_act:
            print(f"  WOULD ENACT: {b['repo']} :: {b['organ']} (r={b['resonance']})")
        return

    enacted, failed, skipped = 0, 0, 0
    for b in to_act:
        r = enact_handler({"action": "enact", "repo": b["repo"], "organ": b["organ"]})
        status = r.get("status")
        if status == "enacted":
            enacted += 1
            print(f"  ✅ {b['repo']} :: {b['organ']} -> {r.get('stone','')}")
        elif status == "already_enacted":
            skipped += 1
        else:
            failed += 1
            print(f"  ❌ {b['repo']} :: {b['organ']} -> {status}")

    print(f"\n=== Summary: {enacted} enacted, {skipped} skipped, {failed} failed ===")
    print(f"  health_index: {s['health_index']}")


if __name__ == "__main__":
    main()
