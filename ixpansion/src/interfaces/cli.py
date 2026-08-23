from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.runtime import IxpansionRuntime


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the IXpansion experimental mesh")
    parser.add_argument("--scene", default="hex_storm", choices=("hex_storm", "mesh_fracture", "overgrowth_field"))
    parser.add_argument("--topology", default="star", choices=("star", "ring", "chaotic"))
    parser.add_argument("--ticks", type=int, default=3)
    parser.add_argument("--compact", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        timeline = IxpansionRuntime(args.scene, args.topology).run(args.ticks)
        if args.compact:
            timeline = [
                {"tick": item["tick"], "fingerprint": item["fingerprint"], "anomalies": item["anomalies"]}
                for item in timeline
            ]
        print(json.dumps(timeline, sort_keys=True, indent=2))
        return 0
    except (KeyError, TypeError, ValueError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
