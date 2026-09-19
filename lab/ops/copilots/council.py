"""Council — run AEGIS + HELIX + QUILL as one continuity loop.

Usage:
  python -m lab.ops.copilots.council
  python lab/ops/copilots/council.py --json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from lab.ops.copilots.aegis import Aegis
from lab.ops.copilots.helix import Helix
from lab.ops.copilots.quill import Quill

OUT = _ROOT / "data" / "copilots" / "council_brief.json"


def run_council() -> dict:
    aegis = Aegis()
    helix = Helix()
    quill = Quill()

    scan = aegis.scan_local()
    triage = aegis.triage()
    growth = helix.growth_brief()
    brief = quill.brief(aegis=scan, helix=growth, extra="three co-pilots online with ALEPH")

    package = {
        "council": ["AEGIS", "HELIX", "QUILL"],
        "alongside": "ALEPH",
        "ts": datetime.now(timezone.utc).isoformat(),
        "aegis": {"scan": scan, "triage": triage},
        "helix": growth,
        "quill": brief,
        "next_moves": [
            scan["actions"][0] if scan.get("actions") else "Hold dual-track",
            f"Scaffold {growth['next']['module']}" if growth.get("next") else "Survey waves",
            "Publish caption / heartbeat via QUILL",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    try:
        OUT.write_text(json.dumps(package, indent=2) + "\n")
    except OSError:
        pass
    return package


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ALEPH co-pilot council")
    parser.add_argument("--json", action="store_true", help="print full JSON")
    args = parser.parse_args(argv)
    package = run_council()
    if args.json:
        print(json.dumps(package, indent=2))
    else:
        print(f"Council · {package['ts']}")
        print(f"  AEGIS posture: {package['aegis']['scan'].get('posture')}")
        print(f"  HELIX next:    {package['helix']['next'].get('module')}")
        print(f"  QUILL head:    {package['quill'].get('headline')}")
        for m in package["next_moves"]:
            print(f"  → {m}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
