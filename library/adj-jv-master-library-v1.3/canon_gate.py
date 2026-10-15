"""Dry-run Canon promotion gate. Never edits the manifest automatically."""
import argparse
import json
from pathlib import Path

from library_validator import load_manifest
from proof_contract import canon_promotion_errors

ROOT = Path(__file__).resolve().parents[3]


def main() -> int:
    parser = argparse.ArgumentParser(description="Check whether an entry is eligible for Canon promotion.")
    parser.add_argument("--entry", required=True, help="Entry ID to evaluate")
    parser.add_argument("--manifest", default=str(Path(__file__).with_name("manifest.json")))
    args = parser.parse_args()
    doc = load_manifest(Path(args.manifest))
    errors = canon_promotion_errors(doc, args.entry, ROOT)
    print(json.dumps({"entry": args.entry, "eligible": not errors, "errors": errors, "mutated": False}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
