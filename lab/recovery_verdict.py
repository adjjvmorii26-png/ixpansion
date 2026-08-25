#!/usr/bin/env python3
"""Recovery Verdict Recorder — seal a human tribunal outcome without execution rights."""
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

from lab.recovery_dossier import dossier_is_sealed
from lab.recovery_treaty import verify_treaty
from lab.runtime_vault import (
    CHAIN_FIELDS,
    append_jsonl,
    ledger_path,
    read_json,
    report_path,
    write_json,
)


SCHEMA = "aleph.chronoforge.recovery-verdict.v1"
MIN_KEY_LENGTH = 16
DECISION_KEY_ENV_ONE = "ALEPH_VERDICT_KEY_ONE"
DECISION_KEY_ENV_TWO = "ALEPH_VERDICT_KEY_TWO"
VERDICTS = {
    "approve": {
        "status": "approved_for_separate_executor_contract",
        "next_action": "draft_independent_executor_contract_for_review",
    },
    "reject": {"status": "rejected", "next_action": "archive_without_execution"},
    "defer": {"status": "deferred", "next_action": "retain_dossier_for_future_tribunal"},
}


def _canonical(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _hash(payload: Any) -> str:
    return hashlib.sha256(_canonical(payload)).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _key(value: str | None, label: str) -> bytes:
    encoded = (value or os.environ.get(label, "")).encode("utf-8")
    if len(encoded) < MIN_KEY_LENGTH:
        raise ValueError(f"{label} must contain at least {MIN_KEY_LENGTH} bytes")
    return encoded


def _fingerprint(key: bytes) -> str:
    return hmac.new(key, b"aleph.recovery-verdict.key-fingerprint.v1", hashlib.sha256).hexdigest()


def _decision_material(
    *,
    dossier: dict[str, Any],
    verdict: str,
    rationale: str,
    operators: list[str],
    nonce: str,
) -> dict[str, Any]:
    treaty = dossier["treaty"]
    return {
        "context": "aleph.recovery-verdict.authorization.v1",
        "dossier_hash": dossier["dossier_hash"],
        "treaty_hash": treaty["treaty_hash"],
        "treaty_id": treaty["treaty_id"],
        "packet_id": treaty["packet"]["packet_id"],
        "action": treaty["packet"]["action"],
        "scene_witness_hash": treaty["scene_witness_hash"],
        "sources": treaty["binding"]["sources"],
        "verdict": verdict,
        "rationale": rationale,
        "operators": operators,
        "nonce": nonce,
    }


def record_verdict(
    dossier: dict[str, Any],
    *,
    verdict: str,
    rationale: str,
    operator_one: str,
    operator_two: str,
    decision_key_one: str | None = None,
    decision_key_two: str | None = None,
    treaty_key_one: str | None = None,
    treaty_key_two: str | None = None,
    ledgers: list[Path] | None = None,
    nonce: str | None = None,
    clock=utc_now,
    record: bool = True,
) -> dict[str, Any]:
    """Bind two juror signatures to an immutable dossier without enabling execution."""
    normalized = verdict.strip().lower()
    if normalized not in VERDICTS:
        raise ValueError("verdict must be one of: approve, reject, defer")
    rationale = " ".join(rationale.split())
    if not 16 <= len(rationale) <= 1000:
        raise ValueError("rationale must contain between 16 and 1000 characters")
    labels = [operator_one.strip()[:100], operator_two.strip()[:100]]
    if not all(labels) or labels[0] == labels[1]:
        raise ValueError("two distinct juror labels are required")
    if not dossier_is_sealed(dossier):
        raise ValueError("recovery dossier is invalid, modified, or unsealed")

    first_decision_key = _key(decision_key_one, DECISION_KEY_ENV_ONE)
    second_decision_key = _key(decision_key_two, DECISION_KEY_ENV_TWO)
    first_fp = _fingerprint(first_decision_key)
    second_fp = _fingerprint(second_decision_key)
    if hmac.compare_digest(first_fp, second_fp):
        raise ValueError("juror keys must be independent")

    treaty = dossier["treaty"]
    treaty_budget = treaty.get("binding", {}).get("lineage_parameters", {}).get(
        "max_operations", 16
    )
    if not verify_treaty(
        treaty,
        ledgers=ledgers,
        key_one=treaty_key_one,
        key_two=treaty_key_two,
        max_operations=treaty_budget,
    ):
        raise ValueError("bound recovery treaty is invalid or its witnesses changed")

    grant = _decision_material(
        dossier=dossier,
        verdict=normalized,
        rationale=rationale,
        operators=labels,
        nonce=nonce or secrets.token_hex(16),
    )
    signatures = []
    for role, operator, key, fingerprint in (
        ("juror_one", labels[0], first_decision_key, first_fp),
        ("juror_two", labels[1], second_decision_key, second_fp),
    ):
        signatures.append({
            "role": role,
            "operator_label": operator,
            "key_fingerprint": fingerprint,
            "signature": hmac.new(key, _canonical(grant), hashlib.sha256).hexdigest(),
        })

    outcome = VERDICTS[normalized]
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "experiment": "recovery-verdict",
        "status": outcome["status"],
        "mode": "manual-human-verdict",
        "verdict": normalized,
        "rationale": rationale,
        "decided_at": clock(),
        "operators": labels,
        "dossier": dossier,
        "decision_binding": {
            "dossier_hash": dossier["dossier_hash"],
            "treaty_hash": treaty["treaty_hash"],
            "sources": treaty["binding"]["sources"],
            "lineage_parameters": dict(treaty["binding"].get("lineage_parameters", {})),
            "nonce": grant["nonce"],
        },
        "authorization": {
            "required_signatures": 2,
            "signature_count": 2,
            "signatures": signatures,
            "execution_enabled": False,
            "live_mutation_budget": 0,
            "compatible_executors": [],
            "executor_contract_required": normalized == "approve",
            "next_permitted_action": outcome["next_action"],
        },
        "guardrails": [
            "A verdict records intent; it never executes mutation.",
            "Approval requires a separately reviewed executor contract.",
            "Any bound source byte change voids the underlying treaty.",
        ],
    }
    result["verdict_hash"] = _hash(result)

    if record:
        write_json(report_path("recovery-verdict.json"), result)
        sealed = append_jsonl(
            ledger_path("recovery-verdicts.jsonl"),
            {key: value for key, value in result.items() if key != "ledger_entry_hash"},
        )
        result["ledger_entry_hash"] = sealed["entry_hash"]
        write_json(report_path("recovery-verdict.json"), result)
    return result


def verify_verdict(
    report: dict[str, Any],
    *,
    ledgers: list[Path] | None = None,
    decision_key_one: str | None = None,
    decision_key_two: str | None = None,
    treaty_key_one: str | None = None,
    treaty_key_two: str | None = None,
) -> bool:
    """Verify both jurors, the sealed dossier, treaty witnesses, and source bytes."""
    expected_status = VERDICTS.get(report.get("verdict", ""), {}).get("status")
    if (
        report.get("schema") != SCHEMA
        or not expected_status
        or report.get("status") != expected_status
    ):
        return False
    claimed = report.get("verdict_hash")
    auth = report.get("authorization", {})
    binding = report.get("decision_binding", {})
    if not claimed or auth.get("signature_count") != 2 or auth.get("execution_enabled") is not False:
        return False
    body = {
        key: value for key, value in report.items()
        if key not in {"verdict_hash", "ledger_entry_hash", *CHAIN_FIELDS}
    }
    if _hash(body) != claimed or not dossier_is_sealed(report.get("dossier", {})):
        return False
    if binding.get("dossier_hash") != report.get("dossier", {}).get("dossier_hash"):
        return False

    treaty = report.get("dossier", {}).get("treaty", {})
    if binding.get("treaty_hash") != treaty.get("treaty_hash"):
        return False
    bound_budget = treaty.get("binding", {}).get("lineage_parameters", {}).get(
        "max_operations", 16
    )
    if not verify_treaty(
        treaty,
        ledgers=ledgers,
        key_one=treaty_key_one,
        key_two=treaty_key_two,
        max_operations=bound_budget,
    ):
        return False

    grant = _decision_material(
        dossier=report["dossier"],
        verdict=report["verdict"],
        rationale=report["rationale"],
        operators=report["operators"],
        nonce=binding["nonce"],
    )
    signatures = {item.get("role"): item for item in auth.get("signatures", [])}
    if set(signatures) != {"juror_one", "juror_two"}:
        return False
    keys = (
        _key(decision_key_one, DECISION_KEY_ENV_ONE),
        _key(decision_key_two, DECISION_KEY_ENV_TWO),
    )
    fingerprints = [_fingerprint(key) for key in keys]
    if hmac.compare_digest(fingerprints[0], fingerprints[1]):
        return False
    for role, key in zip(("juror_one", "juror_two"), keys):
        stored = signatures[role]
        expected = hmac.new(key, _canonical(grant), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(stored.get("signature", ""), expected):
            return False
        if not hmac.compare_digest(stored.get("key_fingerprint", ""), _fingerprint(key)):
            return False
    return True


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    recorder = commands.add_parser("record", help="record a dual-key tribunal verdict")
    recorder.add_argument("--report", type=Path, required=True, help="sealed dossier JSON")
    recorder.add_argument("--verdict", choices=tuple(VERDICTS), required=True)
    recorder.add_argument("--rationale", required=True)
    recorder.add_argument("--operator-one", required=True)
    recorder.add_argument("--operator-two", required=True)
    recorder.add_argument("ledgers", nargs="*", type=Path)
    verifier = commands.add_parser("verify", help="verify a recorded tribunal verdict")
    verifier.add_argument("--report", type=Path, required=True)
    verifier.add_argument("ledgers", nargs="*", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "record":
            dossier = read_json(args.report, {})
            result = record_verdict(
                dossier,
                verdict=args.verdict,
                rationale=args.rationale,
                operator_one=args.operator_one,
                operator_two=args.operator_two,
                ledgers=args.ledgers or None,
            )
        else:
            report = read_json(args.report, {})
            valid = verify_verdict(report, ledgers=args.ledgers or None)
            result = {"ok": valid, "verdict_hash": report.get("verdict_hash")}
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (OSError, TypeError, ValueError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, sort_keys=True, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
