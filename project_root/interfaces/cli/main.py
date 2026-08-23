"""CLI entry point for the project_root engine."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))


def main() -> None:
    parser = argparse.ArgumentParser(description="ALEPH Project Root Engine")
    subparsers = parser.add_subparsers(dest="command")

    agent_parser = subparsers.add_parser("agent", help="Agent operations")
    agent_parser.add_argument("--action", choices=["list", "spawn", "inspect"], default="list")
    agent_parser.add_argument("--species", default="wanderer")

    pipeline_parser = subparsers.add_parser("pipeline", help="Pipeline operations")
    pipeline_parser.add_argument("--action", choices=["run", "status"], default="status")

    sandbox_parser = subparsers.add_parser("sandbox", help="Sandbox operations")
    sandbox_parser.add_argument("--action", choices=["init", "tick", "snapshot"], default="snapshot")
    sandbox_parser.add_argument("--ticks", type=int, default=1)

    args = parser.parse_args()

    if args.command == "agent":
        print(json.dumps({"action": args.action, "species": args.species}, indent=2))
    elif args.command == "pipeline":
        print(json.dumps({"action": args.action}, indent=2))
    elif args.command == "sandbox":
        print(json.dumps({"action": args.action, "ticks": args.ticks}, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
