#!/usr/bin/env python3
"""Mandate Genome Forge — turn verified outcomes into data-only lineages."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import hashlib
import json
from typing import Any

from lab.ritual_parliament import POLICIES, oracle_is_sealed
from lab.runtime_vault import (
    append_jsonl,
    ledger_path,
    read_json,
    read_jsonl,
    report_path,
    verify_jsonl,
)


SCHEMA = "aleph.chronoforge.mandate-genome.v1"
MAX_GENERATION = 12
COMPATIBILITY_RADIUS = 0.35
CHAIN_FIELDS = {"sequence", "previous_hash", "entry_hash"}
TRAIT_NAMES = ("risk_appetite", "patience", "curiosity", "conservation")


def _canonical(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _hash(payload: Any) -> str:
    return hashlib.sha256(_canonical(payload)).hexdigest()


def _clamp(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 5)


def _certificate_is_valid(report: dict[str, Any]) -> bool:
    certificate = report.get("execution_certificate")
    if not certificate:
        return False
    body = {key: value for key, value in report.items() if key != "execution_certificate"}
    return _hash(body) == certificate


def _verify_mandate(report: dict[str, Any], audit: dict[str, Any]) -> None:
    if report.get("schema") != "aleph.chronoforge.reversible-mandate.v1":
        raise ValueError("unsupported mandate schema")
    oracle = report.get("oracle")
    if not isinstance(oracle, dict) or not oracle_is_sealed(oracle):
        raise ValueError("mandate lacks a sealed oracle")
    if report.get("oracle_hash") != oracle.get("oracle_hash"):
        raise ValueError("mandate and oracle identities disagree")
    if not _certificate_is_valid(report):
        raise ValueError("mandate execution certificate is missing or modified")
    if not audit.get("ok"):
        raise ValueError("proof ledger audit failed")

    declared = report.get("witnesses", [])
    actual = {
        record["entry_hash"]: record
        for record in read_jsonl(ledger_path())
        if record.get("type") == "mandate_tick"
        and record.get("parliament_hash") == report.get("parliament_hash")
    }
    declared_hashes = [item.get("entry_hash") for item in declared]
    if len(actual) != len(declared) or len(set(declared_hashes)) != len(declared):
        raise ValueError("witness count disagrees with the proof ledger")
    for witness in declared:
        record = actual.get(witness.get("entry_hash"))
        if (
            record is None
            or record.get("tick") != witness.get("tick")
            or record.get("after_hash") != witness.get("after_hash")
        ):
            raise ValueError("witness identity disagrees with the mandate report")


def _outcome(report: dict[str, Any]) -> str:
    status = report.get("status")
    if status == "sealed":
        return "successful"
    if status == "rehearsed":
        return "dream"
    if status in {"rolled_back", "unverified"}:
        return "quarantined"
    raise ValueError("mandate has no genome-worthy terminal state")


def _average_energy(report: dict[str, Any]) -> float:
    oracle = report["oracle"]
    planned = int(report["planned_ticks"])
    projections = oracle["forecast"]["projections"][:planned]
    multiplier = float(report["directive"]["consumption_multiplier"])
    values = [min(1.0, max(0.0, float(item["energy"]) * multiplier)) for item in projections]
    if not values:
        raise ValueError("directive contains no rehearsed energy samples")
    return sum(values) / len(values)


def _traits(report: dict[str, Any], outcome: str) -> dict[str, float]:
    budget = float(report.get("final_entropy_budget", report.get("ghost_final_budget")))
    energy = _average_energy(report)
    base_risk = {"ration": 0.20, "stabilize": 0.55, "expand": 0.90}[report["chosen_policy"]]
    return {
        "risk_appetite": _clamp(base_risk * 0.70 + (1.0 - budget) * 0.20 + energy * 0.10),
        "patience": _clamp(1.0 - int(report["planned_ticks"]) / 7),
        "curiosity": _clamp(energy),
        "conservation": _clamp(1.0 - budget),
        "resilience": 1.0 if outcome == "successful" else 0.0,
    }


def forge(report: dict[str, Any]) -> dict[str, Any]:
    """Seal one heritable, executable-data archetype from a mandate outcome."""
    audit = verify_jsonl(ledger_path())
    _verify_mandate(report, audit)
    certificate = report["execution_certificate"]
    if any(
        item.get("provenance", {}).get("execution_certificate") == certificate
        for item in load_genomes()
    ):
        raise ValueError("mandate has already been forged")
    outcome = _outcome(report)
    traits = _traits(report, outcome)
    witnesses = report.get("witnesses", [])
    stable = {
        "schema": SCHEMA,
        "experiment": "mandate-genome",
        "status": "sealed",
        "outcome": outcome,
        "breedable": outcome == "successful",
        "policy": report["chosen_policy"],
        "traits": traits,
        "generation": 1,
        "parent_ids": [],
        "genome_id": "",
        "sigil": "",
        "provenance": {
            "parliament_hash": report["parliament_hash"],
            "oracle_hash": report["oracle_hash"],
            "execution_certificate": report["execution_certificate"],
            "witness_hashes": [item["entry_hash"] for item in witnesses],
            "planned_ticks": report["planned_ticks"],
            "final_entropy_budget": report.get(
                "final_entropy_budget", report.get("ghost_final_budget")
            ),
        },
    }
    identity_seed = _hash(stable)
    stable["genome_id"] = f"MG-{identity_seed[:12].upper()}"
    stable["sigil"] = f"0x{identity_seed[-8:].upper()}"
    stable["genome_hash"] = _hash(stable)
    append_jsonl(genome_ledger_path(), stable)
    return stable


def genome_ledger_path() -> Path:
    return ledger_path("genomes.jsonl")


def load_genomes() -> list[dict[str, Any]]:
    """Load and verify every genome, stripping transport chain metadata."""
    path = genome_ledger_path()
    audit = verify_jsonl(path)
    if not audit.get("ok"):
        raise ValueError("genome ledger audit failed")
    genomes = []
    for record in read_jsonl(path):
        clean = {key: value for key, value in record.items() if key not in CHAIN_FIELDS}
        claimed_hash = clean.pop("genome_hash", "")
        if not claimed_hash or _hash(clean) != claimed_hash:
            raise ValueError("genome hash verification failed")
        clean["genome_hash"] = claimed_hash
        genomes.append(clean)
    return genomes


def _stable_genome(genome: dict[str, Any]) -> dict[str, Any]:
    body = {key: value for key, value in genome.items() if key != "genome_hash"}
    if genome.get("status") != "sealed" or genome.get("genome_hash") != _hash(body):
        raise ValueError("genome is missing, unsealed, or modified")
    if genome.get("generation", 99) > MAX_GENERATION:
        raise ValueError("genome exceeds the generation ceiling")
    if int(genome.get("generation", 0)) > 1:
        parent_count = len(genome.get("parent_ids", []))
        if parent_count != 2:
            raise ValueError("bred genome lacks two parents")
    elif genome.get("parent_ids"):
        raise ValueError("first-generation genome cannot declare parents")
    return body


def _compatibility(first: dict[str, Any], second: dict[str, Any]) -> float:
    distance = max(
        abs(float(first["traits"][name]) - float(second["traits"][name]))
        for name in TRAIT_NAMES
    )
    return _clamp(1.0 - distance / 2.0)


def breed(parent_one: dict[str, Any], parent_two: dict[str, Any]) -> dict[str, Any]:
    """Create a deterministic child from two verified, compatible successes."""
    bodies = []
    for parent in (parent_one, parent_two):
        body = _stable_genome(parent)
        if not body.get("breedable") or body.get("outcome") != "successful":
            raise ValueError("only successful genomes are breedable")
        bodies.append({**body, "genome_hash": parent["genome_hash"]})
    ordered = sorted(bodies, key=lambda item: item["genome_id"])
    left, right = ordered
    compatibility = _compatibility(left, right)
    if compatibility < 1.0 - COMPATIBILITY_RADIUS:
        raise ValueError("parent trait distance exceeds the compatibility radius")

    traits = {
        name: _clamp((float(left["traits"][name]) + float(right["traits"][name])) / 2)
        for name in left["traits"]
    }
    differentiation = _clamp((1.0 - compatibility) * 0.08)
    traits["risk_appetite"] = _clamp(traits["risk_appetite"] + differentiation)

    child_policy = min(
        POLICIES,
        key=lambda policy: (
            abs(float(POLICIES[policy]["risk"]) - traits["risk_appetite"]),
            policy,
        ),
    )
    generation = max(int(left["generation"]), int(right["generation"])) + 1
    stable = {
        "schema": SCHEMA,
        "experiment": "mandate-genome",
        "status": "sealed",
        "outcome": "synthesized",
        "breedable": True,
        "policy": child_policy,
        "traits": traits,
        "generation": generation,
        "parent_ids": [left["genome_id"], right["genome_id"]],
        "genome_id": "",
        "sigil": "",
        "compatibility": compatibility,
        "provenance": {
            "parents": [
                {
                    "genome_id": parent["genome_id"],
                    "genome_hash": parent["genome_hash"],
                    "execution_certificate": parent["provenance"]["execution_certificate"],
                }
                for parent in (left, right)
            ],
        },
    }
    identity_seed = _hash(stable)
    stable["genome_id"] = f"MG-{identity_seed[:12].upper()}"
    stable["sigil"] = f"0x{identity_seed[-8:].upper()}"
    stable["genome_hash"] = _hash(stable)
    append_jsonl(genome_ledger_path(), stable)
    return stable


def find_genome(identifier: str, genomes: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    candidates = load_genomes() if genomes is None else genomes
    for genome in candidates:
        if genome["genome_id"] == identifier:
            return genome
    raise ValueError(f"genome not found: {identifier}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    forge_command = commands.add_parser("forge")
    forge_command.add_argument("--report", type=Path, default=None)
    breed_command = commands.add_parser("breed")
    breed_command.add_argument("--parents", required=True, help="two genome IDs separated by a comma")
    commands.add_parser("list")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "forge":
            source = args.report or report_path("reversible-mandate.json")
            result = forge(read_json(source, {}))
        elif args.command == "breed":
            identifiers = [item.strip() for item in args.parents.split(",")]
            if len(identifiers) != 2:
                raise ValueError("--parents requires exactly two genome IDs")
            genomes = load_genomes()
            result = breed(find_genome(identifiers[0], genomes), find_genome(identifiers[1], genomes))
        else:
            result = {"genomes": load_genomes()}
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (KeyError, TypeError, ValueError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, sort_keys=True, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
