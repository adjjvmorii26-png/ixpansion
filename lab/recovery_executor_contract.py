#!/usr/bin/env python3
"""Recovery Executor Contract Forge — draft zero-authority handoffs after approval."""
from __future__ import annotations

import argparse
import hashlib
import hmac
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

from lab.recovery_verdict import verify_verdict
from lab.runtime_vault import (
    CHAIN_FIELDS,
    append_jsonl,
    ledger_path,
    read_json,
    report_path,
    write_json,
)


SCHEMA = "aleph.chronoforge.executor-contract.v1"
MIN_KEY_LENGTH = 16
CONTRACT_KEY_ENV_ONE = "ALEPH_EXECUTOR_CONTRACT_KEY_ONE"
CONTRACT_KEY_ENV_TWO = "ALEPH_EXECUTOR_CONTRACT_KEY_TWO"

CANDIDATE_CAPABILITIES = (
    "read_bound_sources",
    "prepare_change_manifest",
)
PROHIBITED_CAPABILITIES = (
    "execute_commands",
    "mutate_repository",
    "access_networks",
    "expand_permissions",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _hash(payload: dict[str, Any]) -> str:
    material = {key: value for key, value in payload.items() if key != "contract_hash"}
    return hashlib.sha256(_canonical(material)).hexdigest()


def _key(value: str | None, environment_name: str) -> bytes:
    encoded = (value or os.environ.get(environment_name, "")).encode("utf-8")
    if len(encoded) < MIN_KEY_LENGTH:
        raise ValueError(f"a contract key of at least {MIN_KEY_LENGTH} bytes is required")
    return encoded


def _fingerprint(key: bytes) -> str:
    return hmac.new(key, b"aleph.executor-contract.key-fingerprint.v1", hashlib.sha256).hexdigest()


def _contract_proposal(
    verdict: dict[str, Any],
    *,
    nonce: str,
) -> dict[str, Any]:
    dossier = verdict["dossier"]
    treaty = dossier["treaty"]
    binding = treaty["binding"]
    lineage_parameters = dict(binding.get("lineage_parameters", {}))
    packet = dict(treaty["packet"])
    contract_id = f"executor-{_hash({'packet': packet, 'nonce': nonce})[:24]}"
    return {
        "schema": "aleph.chronoforge.executor-contract-proposal.v1",
        "contract_id": contract_id,
        "verdict_hash": verdict["verdict_hash"],
        "verdict_outcome": verdict["verdict"],
        "dossier_hash": dossier["dossier_hash"],
        "treaty_hash": treaty["treaty_hash"],
        "operation_packet": packet,
        "source_witnesses": binding["sources"],
        "lineage_parameters": lineage_parameters,
        "candidate_capabilities": list(CANDIDATE_CAPABILITIES),
        "prohibited_capabilities": list(PROHIBITED_CAPABILITIES),
        "nonce": nonce,
    }


def forge_contract(
    verdict: dict[str, Any],
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
    """Convert an approved verdict into a separately signed, non-executable review draft."""
    if not verify_verdict(
        verdict,
        ledgers=ledgers,
        decision_key_one=decision_key_one,
        decision_key_two=decision_key_two,
        treaty_key_one=treaty_key_one,
        treaty_key_two=treaty_key_two,
    ):
        raise ValueError("approved recovery verdict is invalid or its witnesses changed")
    if verdict.get("verdict") != "approve":
        raise ValueError("only an approved verdict can be drafted as an executor contract")

    first_key = _key(contract_key_one, CONTRACT_KEY_ENV_ONE)
    second_key = _key(contract_key_two, CONTRACT_KEY_ENV_TWO)
    fingerprints = [_fingerprint(first_key), _fingerprint(second_key)]
    if hmac.compare_digest(*fingerprints):
        raise ValueError("contract keys must be independent")

    proposal = _contract_proposal(verdict, nonce=nonce or secrets.token_hex(16))
    signatures = []
    for role, operator_index in (("reviewer_one", 0), ("reviewer_two", 1)):
        signatures.append({
            "role": role,
            "key_fingerprint": fingerprints[operator_index],
            "signature": hmac.new(
                (first_key, second_key)[operator_index],
                _canonical(proposal),
                hashlib.sha256,
            ).hexdigest(),
        })

    result: dict[str, Any] = {
        "schema": SCHEMA,
        "experiment": "recovery-executor-contract",
        "status": "drafted_for_separate_human_review",
        "mode": "zero-authority-handoff",
        "drafted_at": clock(),
        "proposal": proposal,
        "source_verdict": verdict,
        "authorization": {
            "required_signatures": 2,
            "signature_count": 2,
            "signatures": signatures,
            "execution_enabled": False,
            "live_mutation_budget": 0,
            "compatible_executors": [],
            "next_permitted_action": "independent_human_review_of_change_manifest",
        },
        "guardrails": [
            "This draft contains no executor implementation.",
            "Capabilities are proposals and remain inert until a separate human approval.",
            "Every repository mutation remains forbidden by this artifact.",
        ],
    }
    result["contract_hash"] = _hash(result)

    if record:
        write_json(report_path("recovery-executor-contract.json"), result)
        sealed = append_jsonl(
            ledger_path("recovery-executor-contracts.jsonl"),
            {key: value for key, value in result.items() if key != "ledger_entry_hash"},
        )
        result["ledger_entry_hash"] = sealed["entry_hash"]
        write_json(report_path("recovery-executor-contract.json"), result)
    return result


def verify_contract(
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
    """Verify the full approval chain, terminal seal, and both independent reviewers."""
    if report.get("schema") != SCHEMA or report.get("status") != "drafted_for_separate_human_review":
        return False
    claimed = report.get("contract_hash")
    authorization = report.get("authorization", {})
    if not claimed or authorization.get("signature_count") != 2:
        return False
    if authorization.get("execution_enabled") is not False:
        return False
    if authorization.get("compatible_executors") != []:
        return False
    body = {
        key: value for key, value in report.items()
        if key not in {"contract_hash", "ledger_entry_hash", *CHAIN_FIELDS}
    }
    if _hash(body) != claimed:
        return False

    proposal = report.get("proposal", {})
    source_verdict = report.get("source_verdict")
    if not isinstance(source_verdict, dict):
        return False
    if not verify_verdict(
        source_verdict,
        ledgers=ledgers,
        decision_key_one=decision_key_one,
        decision_key_two=decision_key_two,
        treaty_key_one=treaty_key_one,
        treaty_key_two=treaty_key_two,
    ):
        return False
    expected_proposal = _contract_proposal(source_verdict, nonce=proposal.get("nonce", ""))
    if proposal != expected_proposal:
        return False
    if source_verdict.get("authorization", {}).get("executor_contract_required") is not True:
        return False

    signatures = {
        item.get("role"): item for item in authorization.get("signatures", [])
    }
    if set(signatures) != {"reviewer_one", "reviewer_two"}:
        return False
    keys = (
        _key(contract_key_one, CONTRACT_KEY_ENV_ONE),
        _key(contract_key_two, CONTRACT_KEY_ENV_TWO),
    )
    fingerprints = [_fingerprint(keys[0]), _fingerprint(keys[1])]
    if hmac.compare_digest(*fingerprints):
        return False
    for role, key, fingerprint in zip(
        ("reviewer_one", "reviewer_two"), keys, fingerprints
    ):
        stored = signatures[role]
        expected = hmac.new(key, _canonical(proposal), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(stored.get("signature", ""), expected):
            return False
        if not hmac.compare_digest(stored.get("key_fingerprint", ""), fingerprint):
            return False
    return True


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    compiler = commands.add_parser("forge", help="forge a zero-authority executor draft")
    compiler.add_argument("--report", type=Path, required=True, help="approved verdict JSON")
    compiler.add_argument("ledgers", nargs="+", type=Path)
    compiler.add_argument("--no-ledger", action="store_true")
    verifier = commands.add_parser("verify", help="verify an executor contract")
    verifier.add_argument("--report", type=Path, required=True)
    verifier.add_argument("ledgers", nargs="+", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = read_json(args.report, {})
        if not isinstance(report, dict):
            raise ValueError("report must contain a JSON object")
        common = {
            "decision_key_one": os.environ.get("ALEPH_VERDICT_KEY_ONE"),
            "decision_key_two": os.environ.get("ALEPH_VERDICT_KEY_TWO"),
            "treaty_key_one": os.environ.get("ALEPH_TREATY_KEY_ONE"),
            "treaty_key_two": os.environ.get("ALEPH_TREATY_KEY_TWO"),
            "contract_key_one": os.environ.get(CONTRACT_KEY_ENV_ONE),
            "contract_key_two": os.environ.get(CONTRACT_KEY_ENV_TWO),
        }
        if args.command == "forge":
            result = forge_contract(report, ledgers=args.ledgers, record=not args.no_ledger, **common)
        else:
            valid = verify_contract(report, ledgers=args.ledgers, **common)
            result = {"ok": valid}
        json.dump(result, sys.stdout, sort_keys=True, indent=2)
        sys.stdout.write("\n")
        return 0 if args.command == "forge" or result["ok"] else 1
    except (OSError, TypeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
