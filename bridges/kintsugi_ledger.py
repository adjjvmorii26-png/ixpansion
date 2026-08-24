"""Kintsugi Ledger — repair Proof Garden damage without erasing its scars."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bridges.astral_braid import canonical_hash
from bridges.proof_garden import EMPTY_ROOT, ProofEvent, merkle_root

REQUIRED_FIELDS = {
    "kind", "certificate_hash", "selected_strategy", "source_dream_id",
    "source_evidence_hash", "candidate_count", "sequence", "previous_root",
    "root", "ledger_size", "leaf_hash",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def content_hash(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class KintsugiLedgerRepairer:
    """Preserve the longest valid proof chain and archive every damaged byte."""

    clock: Any = utc_now

    @staticmethod
    def _classify(raw: str) -> str:
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            return "malformed_json"
        missing = REQUIRED_FIELDS.difference(value) if isinstance(value, dict) else REQUIRED_FIELDS
        return "incomplete_record" if missing else "invalid_growth_ring"

    @staticmethod
    def _accept(
        record: dict[str, Any],
        sequence: int,
        previous_root: str,
        leaves: list[bytes],
    ) -> None:
        event = ProofEvent(
            kind=record["kind"],
            certificate_hash=record["certificate_hash"],
            selected_strategy=record["selected_strategy"],
            source_dream_id=record["source_dream_id"],
            source_evidence_hash=record["source_evidence_hash"],
            candidate_count=int(record["candidate_count"]),
        )
        leaf = event.leaf()
        expected_root = merkle_root([*leaves, leaf])
        valid = (
            record["sequence"] == sequence
            and record["previous_root"] == previous_root
            and record["ledger_size"] == sequence
            and record["leaf_hash"] == leaf.hex()
            and record["root"] == expected_root
        )
        if not valid:
            raise ValueError("growth ring does not match its ancestry")
        leaves.append(leaf)

    def diagnose(self, ledger: Path) -> dict[str, Any]:
        raw_lines = [
            line for line in ledger.read_text(encoding="utf-8").splitlines() if line.strip()
        ] if ledger.exists() else []
        valid_records: list[dict[str, Any]] = []
        valid_lines: list[str] = []
        leaves: list[bytes] = []
        previous_root = EMPTY_ROOT
        first_fracture: int | None = None

        for index, raw in enumerate(raw_lines):
            try:
                record = json.loads(raw)
                if not isinstance(record, dict):
                    raise ValueError("record is not an object")
                self._accept(record, len(valid_records) + 1, previous_root, leaves)
                valid_records.append(record)
                valid_lines.append(raw)
                previous_root = record["root"]
            except (KeyError, TypeError, ValueError, json.JSONDecodeError):
                first_fracture = index
                break

        fractures = raw_lines[first_fracture:] if first_fracture is not None else []
        return {
            "ledger": str(ledger),
            "integrity": "golden" if not fractures else "fractured",
            "valid_events": len(valid_records),
            "chain_root": previous_root,
            "first_fracture_line": first_fracture + 1 if first_fracture is not None else None,
            "fracture_count": len(fractures),
            "fractures": [
                {
                    "line": index + 1,
                    "classification": self._classify(raw),
                    "content_hash": content_hash(raw),
                    "raw": raw,
                }
                for index, raw in enumerate(fractures, first_fracture if first_fracture is not None else len(raw_lines))
            ],
        }

    def repair(self, ledger: Path) -> dict[str, Any]:
        diagnosis = self.diagnose(ledger)
        if diagnosis["integrity"] == "golden":
            return {"ok": True, "repaired": False, **diagnosis}

        ledger.parent.mkdir(parents=True, exist_ok=True)
        scar_path = ledger.with_name(ledger.name + ".kintsugi.jsonl")
        repaired_at = self.clock()
        scars = []
        for fracture in diagnosis["fractures"]:
            scar = {
                "artifact": ledger.name,
                "line": fracture["line"],
                "classification": fracture["classification"],
                "content_hash": fracture["content_hash"],
                "raw": fracture["raw"],
                "preserved_at": repaired_at,
            }
            scars.append(scar)
        scar_record = {
            "record_type": "kintsugi.fracture",
            "chain_root": diagnosis["chain_root"],
            "preserved_events": diagnosis["valid_events"],
            "fracture_count": diagnosis["fracture_count"],
            "scars": scars,
        }
        with scar_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(scar_record, sort_keys=True, separators=(",", ":")) + "\n")

        temporary = ledger.with_suffix(ledger.suffix + ".kintsugi.tmp")
        temporary.write_text(
            "".join(line + "\n" for line in self._valid_lines(ledger)), encoding="utf-8"
        )
        os.replace(temporary, ledger)

        evidence = canonical_hash({
            "chain_root": diagnosis["chain_root"],
            "preserved_events": diagnosis["valid_events"],
            "fracture_hashes": [item["content_hash"] for item in diagnosis["fractures"]],
        })
        return {
            "ok": True,
            "repaired": True,
            "ledger": str(ledger),
            "scar_ledger": str(scar_path),
            "preserved_events": diagnosis["valid_events"],
            "quarantined_fractures": diagnosis["fracture_count"],
            "chain_root": diagnosis["chain_root"],
            "evidence_hash": evidence,
            "repaired_at": repaired_at,
        }

    @staticmethod
    def _valid_lines(ledger: Path) -> list[str]:
        raw_lines = [line for line in ledger.read_text(encoding="utf-8").splitlines() if line.strip()]
        valid: list[str] = []
        records: list[dict[str, Any]] = []
        leaves: list[bytes] = []
        previous_root = EMPTY_ROOT
        for raw in raw_lines:
            try:
                record = json.loads(raw)
                KintsugiLedgerRepairer._accept(record, len(records) + 1, previous_root, leaves)
            except (KeyError, TypeError, ValueError, json.JSONDecodeError):
                break
            valid.append(raw)
            records.append(record)
            previous_root = record["root"]
        return valid



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Diagnose and repair a fractured Proof Garden")
    parser.add_argument("--ledger", type=Path, default=Path("artifacts/proof-garden.jsonl"))
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("diagnose")
    commands.add_parser("repair")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        repairer = KintsugiLedgerRepairer()
        result = repairer.diagnose(args.ledger) if args.command == "diagnose" else repairer.repair(args.ledger)
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
