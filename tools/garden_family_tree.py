"""Garden Family Tree — render the lineage of every organism (CLI)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from hortus_hexis.lineage import build, export, generations, render_ascii  # noqa: E402


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Render the garden's family tree")
    parser.add_argument("--json", dest="as_json", action="store_true",
                        help="emit JSON instead of ASCII")
    parser.add_argument("--export", action="store_true",
                        help="write family_lineage.json to the garden")
    args = parser.parse_args()

    if args.export:
        p = export()
        print(f"exported lineage to {p}")

    if args.as_json:
        print(json.dumps(generations(), indent=2))
        return
    print(render_ascii())


if __name__ == "__main__":
    main()
