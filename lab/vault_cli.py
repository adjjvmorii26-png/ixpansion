#!/usr/bin/env python3
"""Audit and replay Chrono Forge Runtime Vault ledgers."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import json

from lab.runtime_vault import ledger_path, read_jsonl, verify_jsonl


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    audit = commands.add_parser("verify")
    audit.add_argument("--ledger", type=Path, default=None)
    replay = commands.add_parser("replay")
    replay.add_argument("--ledger", type=Path, default=None)
    replay.add_argument("--depth", type=int, default=10)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    ledger = args.ledger or ledger_path()
    if args.command == "verify":
        result = verify_jsonl(ledger)
    else:
        records = read_jsonl(ledger)[-max(0, args.depth):]
        result = {"schema": "aleph.runtime.ledger.replay.v1", "ledger": str(ledger), "records": records}
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if args.command == "replay" or result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
