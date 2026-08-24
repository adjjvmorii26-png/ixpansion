#!/usr/bin/env python3
"""Evolution Council — turn ancestry, resonance, and diversity into a safe playbook."""
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

from lab.ancestral_echo import _state_signature, echo, echo_is_sealed
from lab.genome_observatory import census
from lab.mandate_genome import MAX_GENERATION, load_genomes
from lab.runtime_vault import (
    append_jsonl,
    ledger_path,
    read_json,
    read_jsonl,
    report_path,
    state_path,
    verify_jsonl,
    write_json,
)


SCHEMA = "aleph.chronoforge.evolution-council.v1"
CHAIN_FIELDS = {"sequence", "previous_hash", "entry_hash"}
ACTION_PRIORITY = {
    "containment_review": 0.95,
    "retire_candidate": 0.72,
    "preserve": 0.80,
    "monitor": 0.58,
    "archive_dream": 0.46,
    "dormancy_review": 0.40,
}


def _canonical(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _hash(payload: Any) -> str:
    return hashlib.sha256(_canonical(payload)).hexdigest()


def _clamp(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 5)


def _load_latest_echoes() -> dict[str, dict[str, Any]]:
    echo_ledger = ledger_path("genome-echoes.jsonl")
    audit = verify_jsonl(echo_ledger)
    if not audit.get("ok"):
        raise ValueError("genome echo ledger audit failed")
    latest: dict[str, tuple[int, dict[str, Any]]] = {}
    for record in read_jsonl(echo_ledger):
        if not echo_is_sealed(record):
            raise ValueError("unsealed or modified genome echo evidence")
        genome_id = record["genome_id"]
        sequence = int(record["sequence"])
        if genome_id not in latest or sequence > latest[genome_id][0]:
            latest[genome_id] = (sequence, record)
    return {identifier: item[1] for identifier, item in latest.items()}


def _action(genome: dict[str, Any], echo_report: dict[str, Any]) -> tuple[str, str, float]:
    verdict = echo_report.get("verdict")
    outcome = genome.get("outcome")
    if outcome == "dream":
        return "archive_dream", "Rehearsal-only lineage retained as evidence; breeding remains forbidden.", 0.46
    if outcome in {"quarantined", "synthesized"} and outcome != "successful":
        return "containment_review", "Non-success lineage requires containment review before any reuse.", 0.95
    if outcome == "quarantined":
        return "containment_review", "Failed execution lineage is preserved for scar review.", 0.95
    if verdict == "resonant":
        return "preserve", "The ancestor remains viable in the present world.", 0.80 + 0.20 * float(echo_report.get("resonance", 0))
    if verdict == "drifting":
        return "monitor", "The ancestor still functions but its behavior is moving away from the present regime.", 0.58
    if verdict == "fossilized":
        return "retire_candidate", "A once-successful ancestor no longer fits the present world.", 0.72
    if verdict == "quarantined":
        return "containment_review", "Present-world rehearsal crossed a safety threshold.", 0.95
    return "dormancy_review", "The present-world parliament could not form an echo quorum.", 0.40


def _office_votes(
    action: str,
    breedable: bool,
    resonance: float,
    warnings: list[dict[str, Any]],
) -> dict[str, str]:
    warning_kinds = {item.get("kind") for item in warnings}
    archivist = "support" if action in {"preserve", "archive_dream", "retire_candidate"} else "review"
    sentinel = (
        "block"
        if action in {"containment_review", "dormancy_review"} or "policy_monoculture" in warning_kinds
        else "support"
    )
    explorer = (
        "support"
        if breedable and action in {"preserve", "monitor"} and resonance >= 0.70
        else "observe"
    )
    return {"archivist": archivist, "sentinel": sentinel, "explorer": explorer}


def deliberate(
    *,
    current_state: dict[str, Any] | None = None,
    record: bool = True,
) -> dict[str, Any]:
    """Create a sealed, advisory-only evolution playbook without mutating genomes."""
    genomes = load_genomes()
    population_report = census(genomes)
    state = read_json(state_path("sandbox", "engine.json"), {}) if current_state is None else current_state
    signature_hash = _hash(_state_signature(state))
    stored_echoes = _load_latest_echoes()

    actions = []
    fresh_echoes: dict[str, dict[str, Any]] = {}
    for genome in sorted(genomes, key=lambda item: item["genome_id"]):
        identifier = genome["genome_id"]
        stored = stored_echoes.get(identifier)
        if stored and stored.get("current_state_signature_hash") == signature_hash:
            echo_report = stored
        else:
            echo_report = echo(identifier, current_state=state, record=False)
        fresh_echoes[identifier] = echo_report
        action, rationale, priority = _action(genome, echo_report)
        votes = _office_votes(action, genome.get("breedable") is True, float(echo_report.get("resonance", 0)), population_report["warnings"])
        support = sum(vote in {"support", "review"} for vote in votes.values())
        actions.append({
            "genome_id": identifier,
            "generation": int(genome.get("generation", 0)),
            "outcome": genome.get("outcome"),
            "policy": genome.get("policy"),
            "echo_verdict": echo_report.get("verdict"),
            "resonance": echo_report.get("resonance"),
            "action": action,
            "priority": _clamp(priority),
            "rationale": rationale,
            "offices": votes,
            "quorum_met": support >= 2,
            "executable": False,
        })

    warning_kinds = {item.get("kind") for item in population_report["warnings"]}
    action_by_id = {item["genome_id"]: item for item in actions}
    candidates = []
    for recommendation in population_report["recommendations"]:
        parent_ids = recommendation["parent_ids"]
        parents = [next(item for item in genomes if item["genome_id"] == identifier) for identifier in parent_ids]
        blockers = []
        if any(action_by_id[item]["action"] != "preserve" for item in parent_ids):
            blockers.append("both parents must currently be preservation actions")
        if any(fresh_echoes[item].get("verdict") != "resonant" for item in parent_ids):
            blockers.append("both parents must have resonant present-world echoes")
        max_parent_generation = max(int(item.get("generation", 0)) for item in parents)
        if "generation_ceiling_pressure" in warning_kinds and max_parent_generation >= MAX_GENERATION - 1:
            blockers.append("generation ceiling pressure")
        if (
            "policy_monoculture" in warning_kinds
            and len({item.get("policy") for item in parents}) == 1
        ):
            blockers.append("same-policy breeding during monoculture pressure")
        intent = {
            "parents": parent_ids,
            "projected_policy": recommendation["projected_policy"],
            "projected_traits": recommendation["projected_traits"],
            "compatibility": recommendation["compatibility"],
        }
        status = "blocked" if blockers else "proposed"
        candidates.append({
            **intent,
            "status": status,
            "blockers": blockers,
            "requires_explicit_consent": status == "proposed",
            "consent_intent_hash": _hash({"action": "breed", **intent}),
            "execution": (
                f"python3 lab/mandate_genome.py breed --parents {parent_ids[0]},{parent_ids[1]}"
                if status == "proposed"
                else None
            ),
        })
    candidates.sort(key=lambda item: (-float(item["compatibility"]), item["parents"]))

    stable = {
        "schema": SCHEMA,
        "experiment": "evolution-council",
        "status": "sealed",
        "mode": "advisory-only",
        "mutation_budget": 0,
        "current_state_signature_hash": signature_hash,
        "sources": {
            "census_hash": population_report["census_hash"],
            "genome_count": len(genomes),
            "stored_echo_count": len(stored_echoes),
            "fresh_echo_count": sum(
                identifier not in stored_echoes
                or stored_echoes[identifier].get("current_state_signature_hash") != signature_hash
                for identifier in fresh_echoes
            ),
        },
        "population": population_report["population"],
        "warnings": population_report["warnings"],
        "actions": sorted(actions, key=lambda item: (-float(item["priority"]), item["genome_id"])),
        "breeding_candidates": candidates,
        "council_quorum": {
            "archivist": any(item["offices"]["archivist"] == "support" for item in actions),
            "sentinel": all(item["offices"]["sentinel"] != "block" or item["action"].startswith("containment") for item in actions),
            "explorer": any(item["offices"]["explorer"] == "support" for item in actions),
            "met": False,
        },
        "guardrails": [
            "No genome, sandbox, or ledger mutation is performed by this council.",
            "Breeding remains forbidden without explicit operator consent.",
            "All evidence must pass terminal hash and ledger-chain verification.",
        ],
    }
    stable["council_quorum"]["met"] = sum(
        value for key, value in stable["council_quorum"].items() if key != "met"
    ) >= 2
    stable["council_hash"] = _hash(stable)

    if record:
        write_json(report_path("evolution-council.json"), stable)
        sealed = append_jsonl(ledger_path("evolution-councils.jsonl"), stable)
        stable["ledger_entry_hash"] = sealed["entry_hash"]
        write_json(report_path("evolution-council.json"), stable)
    return stable


def council_is_sealed(report: dict[str, Any]) -> bool:
    if report.get("schema") != SCHEMA or report.get("status") != "sealed":
        return False
    claimed = report.get("council_hash")
    if not claimed:
        return False
    body = {
        key: value for key, value in report.items()
        if key not in {"council_hash", "ledger_entry_hash", *CHAIN_FIELDS}
    }
    return _hash(body) == claimed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, default=None, help="JSON file containing current sandbox state")
    parser.add_argument("--no-ledger", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        state = read_json(args.state, {}) if args.state else None
        result = deliberate(current_state=state, record=not args.no_ledger)
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (KeyError, TypeError, ValueError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, sort_keys=True, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
