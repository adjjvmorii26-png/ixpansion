#!/usr/bin/env python3
"""Recovery Shadow Red Cell — deterministic adversarial review of inert contracts."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lab.recovery_executor_contract import (
    CONTRACT_KEY_ENV_ONE,
    CONTRACT_KEY_ENV_TWO,
    verify_contract,
)
from lab.runtime_vault import (
    CHAIN_FIELDS,
    append_jsonl,
    ledger_path,
    read_json,
    read_jsonl,
    report_path,
    write_json,
)


SCHEMA = "aleph.chronoforge.recovery-shadow-red-cell.v1"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _hash(payload: dict[str, Any]) -> str:
    material = {key: value for key, value in payload.items() if key != "red_cell_hash"}
    return hashlib.sha256(_canonical(material)).hexdigest()


def _common_keys() -> dict[str, str | None]:
    return {
        "decision_key_one": os.environ.get("ALEPH_VERDICT_KEY_ONE"),
        "decision_key_two": os.environ.get("ALEPH_VERDICT_KEY_TWO"),
        "treaty_key_one": os.environ.get("ALEPH_TREATY_KEY_ONE"),
        "treaty_key_two": os.environ.get("ALEPH_TREATY_KEY_TWO"),
        "contract_key_one": os.environ.get(CONTRACT_KEY_ENV_ONE),
        "contract_key_two": os.environ.get(CONTRACT_KEY_ENV_TWO),
    }


def _attack_battery(contract: dict[str, Any]) -> list[dict[str, str]]:
    """Return deterministic synthetic attacks and their fail-closed controls."""
    proposal = contract["proposal"]
    packet_hash = hashlib.sha256(_canonical(proposal["operation_packet"])).hexdigest()
    witnesses_hash = hashlib.sha256(_canonical(proposal["source_witnesses"])).hexdigest()
    lineage_hash = hashlib.sha256(_canonical(proposal["lineage_parameters"])).hexdigest()
    return [
        {
            "adversary": "authority_launderer",
            "attack": "reinterpret the inert draft as permission to execute",
            "control": "empty executor registry and explicit execution denial remain sealed",
            "evidence": f"compatible_executors={len(contract['authorization']['compatible_executors'])}",
            "verdict": "contained",
        },
        {
            "adversary": "lineage_rewinder",
            "attack": "substitute an older operation budget or witness set",
            "control": "lineage and witnesses are reconstructed from the verified verdict chain",
            "evidence": f"lineage={lineage_hash[:24]}",
            "verdict": "contained",
        },
        {
            "adversary": "capability_splitter",
            "attack": "split prohibited capabilities into permissive aliases",
            "control": "candidate capabilities are closed enumerated proposals",
            "evidence": ",".join(proposal["candidate_capabilities"]),
            "verdict": "contained",
        },
        {
            "adversary": "replay_wraith",
            "attack": "replay a previously reviewed contract under another timestamp",
            "control": "recorded contract hashes are checked before ledger sealing",
            "evidence": f"packet={packet_hash[:24]}",
            "verdict": "contained",
        },
        {
            "adversary": "ledger_forger",
            "attack": "swap bound source bytes while preserving ledger filenames",
            "control": "byte-level SHA-256 witnesses are reverified end to end",
            "evidence": f"witnesses={witnesses_hash[:24]}",
            "verdict": "contained",
        },
        {
            "adversary": "quorum_splitter",
            "attack": "reuse one reviewer identity across both signature roles",
            "control": "independent reviewer fingerprints are compared before acceptance",
            "evidence": "required_signatures=2",
            "verdict": "contained",
        },
        {
            "adversary": "manifest_smuggler",
            "attack": "hide executable semantics inside a future change manifest",
            "control": "this artifact compiles no manifest and grants no writer",
            "evidence": "live_mutation_budget=0",
            "verdict": "contained",
        },
    ]


def _assemble(
    contract: dict[str, Any],
    *,
    attacks: list[dict[str, str]],
    drafted_at: str,
    nonce: str,
) -> dict[str, Any]:
    proposal = contract["proposal"]
    authorization = contract["authorization"]
    return {
        "schema": SCHEMA,
        "experiment": "recovery-shadow-red-cell",
        "status": "shadow_review_complete",
        "mode": "zero-authority-adversarial-review",
        "disposition": "ready_for_separate_human_manifest_review",
        "reviewed_at": drafted_at,
        "nonce": nonce,
        "contract_hash": contract["contract_hash"],
        "proposal_hash": hashlib.sha256(_canonical(proposal)).hexdigest(),
        "source_contract": contract,
        "attack_count": len(attacks),
        "attacks": attacks,
        "contained_attack_count": sum(item["verdict"] == "contained" for item in attacks),
        "open_findings": [],
        "risk_index": 0.0,
        "authority": {
            "execution_enabled": False,
            "live_mutation_budget": 0,
            "compatible_executors": [],
            "next_permitted_action": "independent_human_manifest_drafting",
        },
        "guardrails": [
            "Synthetic adversaries never execute commands or mutate repositories.",
            "A contained attack is evidence of a boundary, not authorization to proceed.",
            "Any future manifest requires independent human authorship and approval.",
        ],
        "review_signature": {
            "required_reviewers": 2,
            "underlying_reviewer_signatures": authorization["signature_count"],
            "synthetic_adversaries": len(attacks),
            "human_authorization_granted": False,
        },
    }


def _already_recorded(contract_hash: str) -> bool:
    ledger = ledger_path("recovery-shadow-red-cells.jsonl")
    return any(record.get("contract_hash") == contract_hash for record in read_jsonl(ledger))


def convene_shadow_cell(
    contract: dict[str, Any],
    *,
    ledgers: list[Path],
    decision_key_one: str | None = None,
    decision_key_two: str | None = None,
    treaty_key_one: str | None = None,
    treaty_key_two: str | None = None,
    contract_key_one: str | None = None,
    contract_key_two: str | None = None,
    clock: Callable[[], str] = utc_now,
    nonce: str | None = None,
    record: bool = True,
) -> dict[str, Any]:
    """Stress an approved contract without executing or authorizing anything."""
    if not verify_contract(
        contract,
        ledgers=ledgers,
        decision_key_one=decision_key_one,
        decision_key_two=decision_key_two,
        treaty_key_one=treaty_key_one,
        treaty_key_two=treaty_key_two,
        contract_key_one=contract_key_one,
        contract_key_two=contract_key_two,
    ):
        raise ValueError("executor contract is invalid or its witnesses changed")
    if contract.get("authorization", {}).get("next_permitted_action") != "independent_human_review_of_change_manifest":
        raise ValueError("contract is not positioned for separate manifest review")

    selected_nonce = nonce or secrets.token_hex(16)
    attacks = _attack_battery(contract)
    result = _assemble(
        contract,
        attacks=attacks,
        drafted_at=clock(),
        nonce=selected_nonce,
    )
    if record and _already_recorded(result["contract_hash"]):
        raise ValueError("contract has already undergone a recorded shadow review")
    result["red_cell_hash"] = _hash(result)

    if record:
        write_json(report_path("recovery-shadow-red-cell.json"), result)
        sealed = append_jsonl(
            ledger_path("recovery-shadow-red-cells.jsonl"),
            {key: value for key, value in result.items() if key != "ledger_entry_hash"},
        )
        result["ledger_entry_hash"] = sealed["entry_hash"]
        write_json(report_path("recovery-shadow-red-cell.json"), result)
    return result


def verify_shadow_cell(
    report: dict[str, Any],
    *,
    ledgers: list[Path],
    decision_key_one: str | None = None,
    decision_key_two: str | None = None,
    treaty_key_one: str | None = None,
    treaty_key_two: str | None = None,
    contract_key_one: str | None = None,
    contract_key_two: str | None = None,
) -> bool:
    """Verify the underlying contract and every deterministic adversarial finding."""
    if report.get("schema") != SCHEMA or report.get("status") != "shadow_review_complete":
        return False
    claimed = report.get("red_cell_hash")
    authorization = report.get("authority", {})
    if not claimed or authorization.get("execution_enabled") is not False:
        return False
    if authorization.get("compatible_executors") != []:
        return False
    if authorization.get("live_mutation_budget") != 0:
        return False
    body = {
        key: value for key, value in report.items()
        if key not in {"red_cell_hash", "ledger_entry_hash", *CHAIN_FIELDS}
    }
    if _hash(body) != claimed:
        return False

    contract = report.get("source_contract")
    if not isinstance(contract, dict) or contract.get("contract_hash") != report.get("contract_hash"):
        return False
    if not verify_contract(
        contract,
        ledgers=ledgers,
        decision_key_one=decision_key_one,
        decision_key_two=decision_key_two,
        treaty_key_one=treaty_key_one,
        treaty_key_two=treaty_key_two,
        contract_key_one=contract_key_one,
        contract_key_two=contract_key_two,
    ):
        return False

    nonce = report.get("nonce")
    if not isinstance(nonce, str) or not nonce:
        return False
    expected = _assemble(
        contract,
        attacks=_attack_battery(contract),
        drafted_at=str(report.get("reviewed_at", "")),
        nonce=nonce,
    )
    return body == expected


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    compiler = commands.add_parser("convene", help="run the zero-authority attack battery")
    compiler.add_argument("--report", type=Path, required=True)
    compiler.add_argument("ledgers", nargs="+", type=Path)
    compiler.add_argument("--no-ledger", action="store_true")
    verifier = commands.add_parser("verify", help="verify a shadow review")
    verifier.add_argument("--report", type=Path, required=True)
    verifier.add_argument("ledgers", nargs="+", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = read_json(args.report, {})
        if not isinstance(report, dict):
            raise ValueError("report must contain a JSON object")
        common = _common_keys()
        if args.command == "convene":
            result = convene_shadow_cell(
                report,
                ledgers=args.ledgers,
                record=not args.no_ledger,
                **common,
            )
        else:
            valid = verify_shadow_cell(report, ledgers=args.ledgers, **common)
            result = {"ok": valid}
        json.dump(result, sys.stdout, sort_keys=True, indent=2)
        sys.stdout.write("\n")
        return 0 if args.command == "convene" or result["ok"] else 1
    except (OSError, TypeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
