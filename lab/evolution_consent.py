#!/usr/bin/env python3
"""Evolution Consent Gate — two-phase human authorization for Council breeding."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timezone
from typing import Any

from lab.evolution_council import council_is_sealed
from lab.mandate_genome import breed
from lab.runtime_vault import (
    append_jsonl,
    ledger_path,
    read_json,
    read_jsonl,
    report_path,
    verify_jsonl,
    write_json,
)


SCHEMA = "aleph.chronoforge.evolution-consent.v1"
CHAIN_FIELDS = {"sequence", "previous_hash", "entry_hash"}
MIN_KEY_LENGTH = 16


def _canonical(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _hash(payload: Any) -> str:
    return hashlib.sha256(_canonical(payload)).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _key(key_env: str) -> tuple[bytes, str]:
    value = os.environ.get(key_env, "")
    if len(value.encode("utf-8")) < MIN_KEY_LENGTH:
        raise ValueError(f"{key_env} must contain at least {MIN_KEY_LENGTH} bytes")
    return value.encode("utf-8"), key_env


def _grant_material(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "action": "breed",
        "candidate_hash": artifact["candidate"]["consent_intent_hash"],
        "council_hash": artifact["council_hash"],
        "parents": artifact["candidate"]["parents"],
        "request_id": artifact["request_id"],
        "nonce": artifact["nonce"],
    }


def _approval_digest(artifact: dict[str, Any], key_env: str) -> str:
    key, _ = _key(key_env)
    return hmac.new(key, _canonical(_grant_material(artifact)), hashlib.sha256).hexdigest()


def _terminal_hash(artifact: dict[str, Any]) -> str:
    body = {
        key: value for key, value in artifact.items()
        if key not in {"consent_hash", "ledger_entry_hash", *CHAIN_FIELDS}
    }
    return _hash(body)


def _finish(artifact: dict[str, Any], *, record: bool, event: str | None = None) -> dict[str, Any]:
    artifact["consent_hash"] = _terminal_hash(artifact)
    if record:
        evidence = {key: value for key, value in artifact.items() if key != "ledger_entry_hash"}
        if event:
            evidence["event"] = event
        sealed_evidence = append_jsonl(ledger_path("evolution-consents.jsonl"), evidence)
        artifact["ledger_entry_hash"] = sealed_evidence["entry_hash"]
        write_json(report_path("evolution-consent.json"), artifact)
    return artifact


def _load_council(source: Path | None) -> dict[str, Any]:
    council = read_json(source or report_path("evolution-council.json"), {})
    if not council_is_sealed(council):
        raise ValueError("council report is missing, unsealed, or modified")
    audit = verify_jsonl(ledger_path("evolution-councils.jsonl"))
    if not audit.get("ok"):
        raise ValueError("evolution council ledger audit failed")
    records = read_jsonl(ledger_path("evolution-councils.jsonl"))
    if not any(record.get("council_hash") == council.get("council_hash") for record in records):
        raise ValueError("council report has no sealed ledger witness")
    return council


def _candidate(council: dict[str, Any], intent_hash: str | None, parents: list[str]) -> dict[str, Any]:
    matches = []
    for item in council.get("breeding_candidates", []):
        correct_intent = intent_hash is None or item.get("consent_intent_hash") == intent_hash
        correct_parents = not parents or item.get("parents") == parents
        if item.get("status") == "proposed" and correct_intent and correct_parents:
            matches.append(item)
    if len(matches) != 1:
        raise ValueError("requested breeding proposal is absent, blocked, or ambiguous")
    return matches[0]


def request(
    *,
    council_source: Path | None = None,
    parents: list[str],
    operator: str,
    intent_hash: str | None = None,
    key_env: str = "ALEPH_CONSENT_KEY",
    clock=utc_now,
) -> dict[str, Any]:
    """Create a pending, keyed authorization request without allowing execution."""
    if not operator.strip():
        raise ValueError("operator label is required")
    council = _load_council(council_source)
    candidate = _candidate(council, intent_hash, parents)
    nonce = secrets.token_hex(16)
    artifact = {
        "schema": SCHEMA,
        "experiment": "evolution-consent",
        "status": "requested",
        "mutation_allowed": False,
        "request_id": "",
        "nonce": nonce,
        "operator_label": operator.strip()[:100],
        "council_hash": council["council_hash"],
        "candidate": {
            **candidate,
            "execution": None,
            "requires_explicit_consent": True,
        },
        "requested_at": clock(),
        "approved_at": None,
        "executed_at": None,
        "approval_digest": None,
        "child_genome_id": None,
        "child_genome_hash": None,
        "key_env": key_env,
        "security_note": "The approval key is never persisted by this module.",
    }
    artifact["request_id"] = f"EC-{_hash({'nonce': nonce, 'council': council['council_hash']})[:16].upper()}"
    digest = _approval_digest(artifact, key_env)
    artifact["approval_digest"] = digest
    return _finish(artifact, record=True, event="requested")


def _verify_ledger_witness(artifact: dict[str, Any]) -> None:
    audit = verify_jsonl(ledger_path("evolution-consents.jsonl"))
    if not audit.get("ok"):
        raise ValueError("evolution consent ledger audit failed")
    expected = {
        key: value for key, value in artifact.items()
        if key not in {"ledger_entry_hash", *CHAIN_FIELDS}
    }
    witnesses = []
    for record in read_jsonl(ledger_path("evolution-consents.jsonl")):
        candidate_witness = {
            key: value for key, value in record.items()
            if key not in {"ledger_entry_hash", "event", *CHAIN_FIELDS}
        }
        if candidate_witness == expected:
            witnesses.append(record)
    if not witnesses:
        raise ValueError("consent report has no matching sealed ledger witness")


def _load_request(request_id: str, expected_status: str) -> dict[str, Any]:
    artifact = read_json(report_path("evolution-consent.json"), {})
    if artifact.get("schema") != SCHEMA or artifact.get("request_id") != request_id:
        raise ValueError("consent request is missing or modified")
    if artifact.get("status") != expected_status:
        raise ValueError(f"consent request is not in {expected_status} state")
    if not _terminal_hash(artifact) == artifact.get("consent_hash"):
        raise ValueError("consent request hash verification failed")
    _verify_ledger_witness(artifact)
    return artifact


def approve(request_id: str, *, key_env: str = "ALEPH_CONSENT_KEY", clock=utc_now) -> dict[str, Any]:
    """Approve a pending request with a separate out-of-band key."""
    artifact = _load_request(request_id, "requested")
    supplied = _approval_digest(artifact, key_env)
    if not hmac.compare_digest(supplied, str(artifact.get("approval_digest"))):
        raise ValueError("approval key does not match the pending request")
    audit = verify_jsonl(ledger_path("evolution-consents.jsonl"))
    if not audit.get("ok"):
        raise ValueError("evolution consent ledger audit failed")
    artifact.update({
        "status": "approved",
        "approved_at": clock(),
        "mutation_allowed": True,
    })
    return _finish(artifact, record=True, event="approved")


def execute(request_id: str, *, clock=utc_now) -> dict[str, Any]:
    """Execute exactly one previously approved breeding proposal."""
    artifact = _load_request(request_id, "approved")
    council = _load_council(None)
    if council.get("council_hash") != artifact.get("council_hash"):
        raise ValueError("approved council no longer matches the consent artifact")
    candidates = [
        item for item in council.get("breeding_candidates", [])
        if item.get("consent_intent_hash") == artifact["candidate"]["consent_intent_hash"]
        and item.get("status") == "proposed"
    ]
    if len(candidates) != 1:
        raise ValueError("approved proposal is no longer available")

    child = breed(
        next(item for item in load_current_genomes() if item["genome_id"] == artifact["candidate"]["parents"][0]),
        next(item for item in load_current_genomes() if item["genome_id"] == artifact["candidate"]["parents"][1]),
    )
    audit = verify_jsonl(ledger_path("genomes.jsonl"))
    if not audit.get("ok") or child["genome_hash"] not in {record.get("genome_hash") for record in read_jsonl(ledger_path("genomes.jsonl"))}:
        raise RuntimeError("bred genome failed post-execution ledger verification")
    artifact.update({
        "status": "executed",
        "mutation_allowed": False,
        "executed_at": clock(),
        "child_genome_id": child["genome_id"],
        "child_genome_hash": child["genome_hash"],
    })
    return _finish(artifact, record=True, event="executed")


def load_current_genomes() -> list[dict[str, Any]]:
    from lab.mandate_genome import load_genomes
    return load_genomes()


def consent_is_sealed(artifact: dict[str, Any]) -> bool:
    if artifact.get("schema") != SCHEMA or not artifact.get("consent_hash"):
        return False
    return _terminal_hash(artifact) == artifact["consent_hash"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    request_command = commands.add_parser("request")
    request_command.add_argument("--parents", required=True, help="two genome IDs separated by a comma")
    request_command.add_argument("--operator", required=True)
    request_command.add_argument("--intent-hash", default=None)
    request_command.add_argument("--council", type=Path, default=None)
    request_command.add_argument("--key-env", default="ALEPH_CONSENT_KEY")

    approve_command = commands.add_parser("approve")
    approve_command.add_argument("request_id")
    approve_command.add_argument("--key-env", default="ALEPH_CONSENT_KEY")

    execute_command = commands.add_parser("execute")
    execute_command.add_argument("request_id")

    commands.add_parser("status")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "request":
            parents = [item.strip() for item in args.parents.split(",")]
            if len(parents) != 2:
                raise ValueError("--parents requires exactly two genome IDs")
            result = request(parents=parents, operator=args.operator, intent_hash=args.intent_hash, council_source=args.council, key_env=args.key_env)
        elif args.command == "approve":
            result = approve(args.request_id, key_env=args.key_env)
        elif args.command == "execute":
            result = execute(args.request_id)
        else:
            result = read_json(report_path("evolution-consent.json"), {"status": "absent"})
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (KeyError, TypeError, ValueError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, sort_keys=True, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
