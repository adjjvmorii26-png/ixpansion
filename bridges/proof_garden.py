"""Proof Garden — grow portable Merkle evidence from Astral Braid decisions."""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bridges.astral_braid import canonical_hash


def leaf_digest(value: bytes) -> bytes:
    return hashlib.sha256(b"aleph-proof-garden\x00" + value).digest()


def merkle_root(leaf_hashes: list[bytes]) -> str:
    """Return a deterministic Merkle root, duplicating a lonely final leaf."""
    if not leaf_hashes:
        return leaf_digest(b"genesis").hex()
    layer = list(leaf_hashes)
    while len(layer) > 1:
        parent: list[bytes] = []
        for index in range(0, len(layer), 2):
            left = layer[index]
            right = layer[index + 1] if index + 1 < len(layer) else left
            parent.append(hashlib.sha256(left + right).digest())
        layer = parent
    return layer[0].hex()


def merkle_proof(leaf_hashes: list[bytes], index: int) -> list[str]:
    """Build an audit path for one leaf within this exact leaf population."""
    if index < 0 or index >= len(leaf_hashes):
        raise ValueError("proof index is outside the ledger")
    proof: list[str] = []
    level = list(leaf_hashes)
    position = index
    while len(level) > 1:
        sibling = position + 1 if position % 2 == 0 else position - 1
        sibling = min(sibling, len(level) - 1)
        proof.append(level[sibling].hex())
        level = [
            hashlib.sha256(level[i] + (level[i + 1] if i + 1 < len(level) else level[i])).digest()
            for i in range(0, len(level), 2)
        ]
        position //= 2
    return proof


def verify_proof(leaf_hash: bytes, proof: list[str], root: str, index: int) -> bool:
    """Verify an audit path without access to the other ledger entries."""
    if index < 0:
        return False
    current = leaf_hash
    position = index
    for item in proof:
        try:
            sibling = bytes.fromhex(item)
        except ValueError:
            return False
        if len(sibling) != 32:
            return False
        if position % 2 == 0:
            current = hashlib.sha256(current + sibling).digest()
        else:
            current = hashlib.sha256(sibling + current).digest()
        position //= 2
    return current.hex() == root


EMPTY_ROOT = merkle_root([])


@dataclass(frozen=True)
class ProofEvent:
    """The minimal, immutable meaning of one conservatory decision."""

    kind: str
    certificate_hash: str
    selected_strategy: str | None
    source_dream_id: str
    source_evidence_hash: str
    candidate_count: int

    @classmethod
    def from_braid_report(cls, report: dict[str, Any]) -> "ProofEvent":
        if report.get("experiment") != "astral-braid-conservatory":
            raise ValueError("report was not produced by astral-braid-conservatory")
        stable_report = {
            key: value for key, value in report.items()
            if key not in ("certificate_hash", "emitted", "performed_at")
        }
        if canonical_hash(stable_report) != report.get("certificate_hash"):
            raise ValueError("certificate hash does not match braid report")

        selected = report.get("selected_strategy")
        if selected is not None and selected not in {"conservative", "lateral", "paradox"}:
            raise ValueError("unknown selected strategy")
        candidates = report.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            raise ValueError("braid report has no rehearsed candidates")
        required = ("certificate_hash", "source_dream_id", "source_evidence_hash")
        if any(not isinstance(report.get(key), str) or not report[key] for key in required):
            raise ValueError("braid report lacks stable identity evidence")

        return cls(
            kind="braid.promoted" if selected is not None else "braid.quarantined",
            certificate_hash=report["certificate_hash"],
            selected_strategy=selected,
            source_dream_id=report["source_dream_id"],
            source_evidence_hash=report["source_evidence_hash"],
            candidate_count=len(candidates),
        )

    def payload(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "certificate_hash": self.certificate_hash,
            "selected_strategy": self.selected_strategy,
            "source_dream_id": self.source_dream_id,
            "source_evidence_hash": self.source_evidence_hash,
            "candidate_count": self.candidate_count,
        }

    def leaf(self) -> bytes:
        encoded = json.dumps(
            self.payload(), sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        return leaf_digest(encoded)


class ProofGarden:
    """Append-only growth rings with independently verifiable pollen packets."""

    schema_version = 1

    def __init__(self, ledger: Path, *, clock: Any = None) -> None:
        self.ledger = ledger
        self.clock = clock or (lambda: datetime.now(timezone.utc).isoformat())

    def _load_and_verify(self) -> list[dict[str, Any]]:
        if not self.ledger.exists():
            return []
        records: list[dict[str, Any]] = []
        leaves: list[bytes] = []
        previous_root = EMPTY_ROOT
        for line_number, line in enumerate(self.ledger.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"invalid proof JSON on line {line_number}") from error
            expected_sequence = len(records) + 1
            try:
                event = ProofEvent(
                    kind=record["kind"],
                    certificate_hash=record["certificate_hash"],
                    selected_strategy=record["selected_strategy"],
                    source_dream_id=record["source_dream_id"],
                    source_evidence_hash=record["source_evidence_hash"],
                    candidate_count=int(record["candidate_count"]),
                )
                valid = (
                    record["sequence"] == expected_sequence
                    and record["previous_root"] == previous_root
                    and record["ledger_size"] == expected_sequence
                    and record["leaf_hash"] == event.leaf().hex()
                    and record["root"] == merkle_root([*leaves, event.leaf()])
                )
            except (KeyError, TypeError, ValueError):
                valid = False
            if not valid:
                raise ValueError(f"proof growth ring {expected_sequence} failed verification")
            leaves.append(event.leaf())
            previous_root = record["root"]
            records.append(record)
        return records

    def plant(self, report: dict[str, Any]) -> dict[str, Any]:
        records = self._load_and_verify()
        event = ProofEvent.from_braid_report(report)
        leaves = [ProofEvent(**{key: record[key] for key in (
            "kind", "certificate_hash", "selected_strategy", "source_dream_id",
            "source_evidence_hash", "candidate_count",
        )}).leaf() for record in records]
        previous_root = records[-1]["root"] if records else EMPTY_ROOT
        leaves.append(event.leaf())
        sequence = len(records) + 1
        record = {
            **event.payload(),
            "sequence": sequence,
            "previous_root": previous_root,
            "root": merkle_root(leaves),
            "ledger_size": len(leaves),
            "recorded_at": self.clock(),
            "leaf_hash": event.leaf().hex(),
        }
        self.ledger.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
        packet = self.prove(sequence)
        return {"record": record, "packet": packet, "verified": True}

    def prove(self, sequence: int) -> dict[str, Any]:
        records = self._load_and_verify()
        if sequence < 1 or sequence > len(records):
            raise ValueError("sequence does not exist in the proof ledger")
        record = records[sequence - 1]
        leaves = []
        for item in records[:sequence]:
            event = ProofEvent(
                kind=item["kind"],
                certificate_hash=item["certificate_hash"],
                selected_strategy=item["selected_strategy"],
                source_dream_id=item["source_dream_id"],
                source_evidence_hash=item["source_evidence_hash"],
                candidate_count=int(item["candidate_count"]),
            )
            leaves.append(event.leaf())
        return {
            "schema": f"aleph.proof-garden.packet.v{self.schema_version}",
            "index": sequence - 1,
            "ledger_size": len(leaves),
            "root": record["root"],
            "leaf_hash": record["leaf_hash"],
            "audit_proof": merkle_proof(leaves, sequence - 1),
            "event": ProofEvent(
                kind=record["kind"],
                certificate_hash=record["certificate_hash"],
                selected_strategy=record["selected_strategy"],
                source_dream_id=record["source_dream_id"],
                source_evidence_hash=record["source_evidence_hash"],
                candidate_count=int(record["candidate_count"]),
            ).payload(),
        }

    def verify_packet(self, packet: dict[str, Any]) -> dict[str, Any]:
        event = ProofEvent(
            kind=packet["event"]["kind"],
            certificate_hash=packet["event"]["certificate_hash"],
            selected_strategy=packet["event"]["selected_strategy"],
            source_dream_id=packet["event"]["source_dream_id"],
            source_evidence_hash=packet["event"]["source_evidence_hash"],
            candidate_count=int(packet["event"]["candidate_count"]),
        )
        verified = (
            event.leaf().hex() == packet.get("leaf_hash")
            and verify_proof(
                event.leaf(),
                packet.get("audit_proof", []),
                packet.get("root", ""),
                int(packet.get("index", -1)),
            )
        )
        if not verified:
            raise ValueError("pollen packet failed Merkle verification")
        return {
            "verified": True,
            "schema": packet.get("schema"),
            "root": packet["root"],
            "index": packet["index"],
            "ledger_size": packet["ledger_size"],
        }

    def audit(self) -> dict[str, Any]:
        records = self._load_and_verify()
        return {
            "verified": True,
            "events": len(records),
            "latest_root": records[-1]["root"] if records else EMPTY_ROOT,
            "promoted": sum(record["kind"] == "braid.promoted" for record in records),
            "quarantined": sum(record["kind"] == "braid.quarantined" for record in records),
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Grow and verify ritual proof evidence")
    parser.add_argument("--ledger", type=Path, default=Path("runs/proof-garden.jsonl"))
    commands = parser.add_subparsers(dest="command", required=True)
    plant = commands.add_parser("plant", help="append one Astral Braid report")
    plant.add_argument("--report", type=Path, required=True)
    plant.add_argument("--output", type=Path)
    prove = commands.add_parser("prove", help="export one portable inclusion proof")
    prove.add_argument("--sequence", type=int, required=True)
    prove.add_argument("--output", type=Path)
    commands.add_parser("audit", help="verify every growth ring")
    verify = commands.add_parser("verify", help="verify a pollen packet")
    verify.add_argument("--packet", type=Path, required=True)
    return parser


def _emit(value: dict[str, Any], output: Path | None) -> None:
    rendered = json.dumps(value, sort_keys=True, indent=2) + "\n"
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    garden = ProofGarden(args.ledger)
    try:
        if args.command == "plant":
            report = json.loads(args.report.read_text(encoding="utf-8"))
            _emit(garden.plant(report), args.output)
        elif args.command == "prove":
            _emit(garden.prove(args.sequence), args.output)
        elif args.command == "audit":
            _emit(garden.audit(), None)
        else:
            packet = json.loads(args.packet.read_text(encoding="utf-8"))
            _emit(garden.verify_packet(packet), None)
        return 0
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
