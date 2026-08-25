#!/usr/bin/env python3
"""Recovery Answer Crucible — seal independent answers to manifest review lenses."""
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

from lab.recovery_manifest_loom import SCHEMA as MANIFEST_SCHEMA, verify_weave
from lab.runtime_vault import (
    CHAIN_FIELDS,
    append_jsonl,
    ledger_path,
    read_json,
    read_jsonl,
    report_path,
    write_json,
)


SCHEMA = "aleph.chronoforge.recovery-answer-crucible.v1"
MIN_KEY_LENGTH = 16
KEY_ENV_ONE = "ALEPH_ANSWER_CRUCIBLE_KEY_ONE"
KEY_ENV_TWO = "ALEPH_ANSWER_CRUCIBLE_KEY_TWO"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _hash(payload: dict[str, Any]) -> str:
    material = {key: value for key, value in payload.items() if key != "crucible_hash"}
    return hashlib.sha256(_canonical(material)).hexdigest()


def _key(value: str | None, environment_name: str) -> bytes:
    encoded = (value or os.environ.get(environment_name, "")).encode("utf-8")
    if len(encoded) < MIN_KEY_LENGTH:
        raise ValueError(f"{environment_name} must contain at least {MIN_KEY_LENGTH} bytes")
    return encoded


def _fingerprint(key: bytes) -> str:
    return hmac.new(key, b"aleph.recovery-answer-crucible.key-fingerprint.v1", hashlib.sha256).hexdigest()


def _text(value: Any, label: str, minimum: int = 20, maximum: int = 500) -> str:
    normalized = " ".join(str(value).split())
    if not minimum <= len(normalized) <= maximum:
        raise ValueError(f"{label} must contain {minimum} to {maximum} characters")
    return normalized


def _validate_answers(raw: Any, threads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Validate one structured response for every sealed provenance lens."""
    if not isinstance(raw, list) or len(raw) != len(threads):
        raise ValueError("answers must contain exactly one entry per intent thread")
    validated = []
    seen = set()
    for index, entry in enumerate(raw):
        if not isinstance(entry, dict):
            raise ValueError(f"answer set {index + 1} must be an object")
        required = {"thread_id", "bound_ledger", "answers"}
        if set(entry) != required:
            raise ValueError(f"answer set {index + 1} must contain exactly {sorted(required)}")
        thread_id = str(entry["thread_id"])
        bound_ledger = str(entry["bound_ledger"])
        answers = entry["answers"]
        matching_thread = next((item for item in threads if item["thread_id"] == thread_id), None)
        if matching_thread is None:
            raise ValueError(f"unknown intent thread: {thread_id}")
        if thread_id in seen:
            raise ValueError(f"duplicate answers for intent thread: {thread_id}")
        if bound_ledger != matching_thread["bound_ledger"]:
            raise ValueError(f"bound ledger mismatch for intent thread: {thread_id}")
        if not isinstance(answers, list) or len(answers) != len(matching_thread["review_lenses"]):
            raise ValueError(f"intent thread {thread_id} requires exactly three answers")

        normalized_answers = []
        expected_lenses = [item["lens"] for item in matching_thread["review_lenses"]]
        actual_lenses = []
        for answer_index, answer in enumerate(answers):
            if not isinstance(answer, dict):
                raise ValueError(f"{thread_id} answer {answer_index + 1} must be an object")
            lens = str(answer.get("lens", ""))
            actual_lenses.append(lens)
            normalized = dict(answer)
            if lens == "provenance":
                if set(answer) != {"lens", "observed_bytes_sha256", "observation_note"}:
                    raise ValueError(f"{thread_id} provenance answer has an invalid shape")
                digest = str(answer["observed_bytes_sha256"]).lower()
                if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
                    raise ValueError(f"{thread_id} provenance answer needs a lowercase SHA-256 digest")
                normalized["observed_bytes_sha256"] = digest
                normalized["observation_note"] = _text(
                    answer["observation_note"], f"{thread_id} observation note", 30, 500
                )
            elif lens == "consequence":
                if set(answer) != {
                    "lens",
                    "observable_signal",
                    "containment_boundary",
                    "side_effect_declaration",
                }:
                    raise ValueError(f"{thread_id} consequence answer has an invalid shape")
                normalized["observable_signal"] = _text(
                    answer["observable_signal"], f"{thread_id} observable signal", 25, 400
                )
                normalized["containment_boundary"] = _text(
                    answer["containment_boundary"], f"{thread_id} containment boundary", 25, 400
                )
                declaration = str(answer["side_effect_declaration"])
                if declaration != "none_observed_during_offline_review":
                    raise ValueError(f"{thread_id} side-effect declaration is invalid")
            elif lens == "reversibility":
                if set(answer) != {
                    "lens",
                    "preservation_method",
                    "human_restorer",
                    "review_window_days",
                }:
                    raise ValueError(f"{thread_id} reversibility answer has an invalid shape")
                normalized["preservation_method"] = _text(
                    answer["preservation_method"], f"{thread_id} preservation method", 25, 400
                )
                restorer = " ".join(str(answer["human_restorer"]).split())
                if not 3 <= len(restorer) <= 100:
                    raise ValueError(f"{thread_id} human restorer label is invalid")
                try:
                    window = int(answer["review_window_days"])
                except (TypeError, ValueError) as error:
                    raise ValueError(f"{thread_id} review window must be an integer") from error
                if not 1 <= window <= 365:
                    raise ValueError(f"{thread_id} review window must be between 1 and 365 days")
                normalized["human_restorer"] = restorer
                normalized["review_window_days"] = window
            else:
                raise ValueError(f"unknown review lens in {thread_id}: {lens}")
            normalized_answers.append(normalized)
        if actual_lenses != expected_lenses:
            raise ValueError(f"answer lenses do not match sealed order for {thread_id}")
        seen.add(thread_id)
        validated.append({
            "thread_id": thread_id,
            "bound_ledger": bound_ledger,
            "answers": normalized_answers,
        })
    return validated


def _assert_provenance(answers: list[dict[str, Any]], weave: dict[str, Any]) -> None:
    witness_digests = {
        item["ledger"]: item["bytes_sha256"]
        for item in weave.get("bound_witnesses", [])
    }
    for entry in answers:
        claimed = next(
            item["observed_bytes_sha256"]
            for item in entry["answers"]
            if item["lens"] == "provenance"
        )
        expected = witness_digests.get(entry["bound_ledger"])
        if expected is None or not hmac.compare_digest(claimed, expected):
            raise ValueError(
                f"provenance answer does not reproduce immutable bytes for {entry['bound_ledger']}"
            )


def _core(
    weave: dict[str, Any],
    *,
    answer_set: list[dict[str, Any]],
    operators: list[str],
    nonce: str,
    answered_at: str,
) -> dict[str, Any]:
    crucible_seed = {
        "manifest_id": weave["manifest_id"],
        "answer_set": answer_set,
        "operators": operators,
        "nonce": nonce,
    }
    return {
        "schema": SCHEMA,
        "experiment": "recovery-answer-crucible",
        "status": "sealed_for_implementation_review",
        "mode": "zero-authority-human-answer-sealing",
        "disposition": "ready_for_independent_manifest_implementation_review",
        "answered_at": answered_at,
        "nonce": nonce,
        "source_weave": weave,
        "manifest_id": weave["manifest_id"],
        "crucible_id": f"crucible-{_hash(crucible_seed)[:24]}",
        "operators": operators,
        "shadow_hash": weave["shadow_hash"],
        "contract_hash": weave["contract_hash"],
        "verdict_hash": weave["verdict_hash"],
        "lineage_parameters": dict(weave["lineage_parameters"]),
        "bound_witnesses": list(weave["bound_witnesses"]),
        "answer_set": answer_set,
        "answer_count": sum(len(item["answers"]) for item in answer_set),
        "provenance_digest_matches": len(answer_set),
        "open_questions": [],
        "authority": {
            "execution_enabled": False,
            "live_mutation_budget": 0,
            "compatible_executors": [],
            "next_permitted_action": "independent_human_drafting_of_implementation_review_packet",
        },
        "guardrails": [
            "Answers document offline human observations only.",
            "A matching provenance digest proves byte awareness, never mutation permission.",
            "No answer, signature, or readiness verdict creates an executor.",
        ],
    }


def _already_recorded(crucible_id: str) -> bool:
    ledger = ledger_path("recovery-answer-crucibles.jsonl")
    return any(record.get("crucible_id") == crucible_id for record in read_jsonl(ledger))


def seal_answers(
    weave: dict[str, Any],
    *,
    answers: list[dict[str, Any]],
    operator_one: str,
    operator_two: str,
    ledgers: list[Path],
    decision_key_one: str | None = None,
    decision_key_two: str | None = None,
    treaty_key_one: str | None = None,
    treaty_key_two: str | None = None,
    contract_key_one: str | None = None,
    contract_key_two: str | None = None,
    loom_key_one: str | None = None,
    loom_key_two: str | None = None,
    crucible_key_one: str | None = None,
    crucible_key_two: str | None = None,
    clock: Callable[[], str] = utc_now,
    nonce: str | None = None,
    record: bool = True,
) -> dict[str, Any]:
    """Seal two-operator responses after full Manifest Loom reverification."""
    if weave.get("schema") != MANIFEST_SCHEMA or weave.get("disposition") != "ready_for_independent_human_answers":
        raise ValueError("a verified Manifest Loom report is required")
    if not verify_weave(
        weave,
        ledgers=ledgers,
        decision_key_one=decision_key_one,
        decision_key_two=decision_key_two,
        treaty_key_one=treaty_key_one,
        treaty_key_two=treaty_key_two,
        contract_key_one=contract_key_one,
        contract_key_two=contract_key_two,
        loom_key_one=loom_key_one,
        loom_key_two=loom_key_two,
    ):
        raise ValueError("Manifest Loom report is invalid or its witnesses changed")

    labels = [operator_one.strip()[:100], operator_two.strip()[:100]]
    if not all(labels) or labels[0] == labels[1]:
        raise ValueError("two distinct answer operator labels are required")
    if set(labels) & set(weave.get("operators", [])):
        raise ValueError("answer operators must be independent of manifest authors")

    first_key = _key(crucible_key_one, KEY_ENV_ONE)
    second_key = _key(crucible_key_two, KEY_ENV_TWO)
    fingerprints = [_fingerprint(first_key), _fingerprint(second_key)]
    if hmac.compare_digest(*fingerprints):
        raise ValueError("answer crucible keys must be independent")

    validated = _validate_answers(answers, weave.get("threads", []))
    _assert_provenance(validated, weave)
    selected_nonce = nonce or secrets.token_hex(16)
    core = _core(
        weave,
        answer_set=validated,
        operators=labels,
        nonce=selected_nonce,
        answered_at=clock(),
    )
    keys = (first_key, second_key)
    signatures = []
    for role, operator_index in zip(("responder_one", "responder_two"), (0, 1)):
        signatures.append({
            "role": role,
            "operator_label": labels[operator_index],
            "key_fingerprint": fingerprints[operator_index],
            "signature": hmac.new(keys[operator_index], _canonical(core), hashlib.sha256).hexdigest(),
        })
    core["authorization"] = {
        "required_signatures": 2,
        "signature_count": 2,
        "signatures": signatures,
        **core["authority"],
    }

    if record and _already_recorded(core["crucible_id"]):
        raise ValueError("answer crucible has already been recorded")
    core["crucible_hash"] = _hash(core)

    if record:
        write_json(report_path("recovery-answer-crucible.json"), core)
        sealed = append_jsonl(
            ledger_path("recovery-answer-crucibles.jsonl"),
            {key: value for key, value in core.items() if key != "ledger_entry_hash"},
        )
        core["ledger_entry_hash"] = sealed["entry_hash"]
        write_json(report_path("recovery-answer-crucible.json"), core)
    return core


def verify_sealed_answers(
    report: dict[str, Any],
    *,
    ledgers: list[Path],
    decision_key_one: str | None = None,
    decision_key_two: str | None = None,
    treaty_key_one: str | None = None,
    treaty_key_two: str | None = None,
    contract_key_one: str | None = None,
    contract_key_two: str | None = None,
    loom_key_one: str | None = None,
    loom_key_two: str | None = None,
    crucible_key_one: str | None = None,
    crucible_key_two: str | None = None,
) -> bool:
    """Verify both responders, every answer, provenance digests, and the upstream chain."""
    if report.get("schema") != SCHEMA or report.get("status") != "sealed_for_implementation_review":
        return False
    claimed = report.get("crucible_hash")
    authorization = report.get("authorization", {})
    if not claimed or authorization.get("signature_count") != 2:
        return False
    if authorization.get("execution_enabled") is not False:
        return False
    if authorization.get("compatible_executors") != []:
        return False
    body = {
        key: value for key, value in report.items()
        if key not in {"crucible_hash", "ledger_entry_hash", *CHAIN_FIELDS}
    }
    if _hash(body) != claimed:
        return False

    weave = report.get("source_weave")
    if not isinstance(weave, dict):
        return False
    if not verify_weave(
        weave,
        ledgers=ledgers,
        decision_key_one=decision_key_one,
        decision_key_two=decision_key_two,
        treaty_key_one=treaty_key_one,
        treaty_key_two=treaty_key_two,
        contract_key_one=contract_key_one,
        contract_key_two=contract_key_two,
        loom_key_one=loom_key_one,
        loom_key_two=loom_key_two,
    ):
        return False

    try:
        validated = _validate_answers(report.get("answer_set"), weave.get("threads", []))
        _assert_provenance(validated, weave)
        expected = _core(
            weave,
            answer_set=validated,
            operators=list(report.get("operators", [])),
            nonce=str(report.get("nonce", "")),
            answered_at=str(report.get("answered_at", "")),
        )
    except (KeyError, TypeError, ValueError):
        return False
    unsigned_body = {key: value for key, value in body.items() if key != "authorization"}
    if unsigned_body != expected:
        return False

    signatures = {item.get("role"): item for item in authorization.get("signatures", [])}
    if set(signatures) != {"responder_one", "responder_two"}:
        return False
    keys = (_key(crucible_key_one, KEY_ENV_ONE), _key(crucible_key_two, KEY_ENV_TWO))
    fingerprints = [_fingerprint(keys[0]), _fingerprint(keys[1])]
    if hmac.compare_digest(*fingerprints):
        return False
    for role, key, fingerprint in zip(("responder_one", "responder_two"), keys, fingerprints):
        stored = signatures[role]
        expected_signature = hmac.new(key, _canonical(unsigned_body), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(stored.get("signature", ""), expected_signature):
            return False
        if not hmac.compare_digest(stored.get("key_fingerprint", ""), fingerprint):
            return False
        if stored.get("operator_label") not in report.get("operators", []):
            return False
    return True


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    sealer = commands.add_parser("seal", help="seal structured answers to all lenses")
    sealer.add_argument("--report", type=Path, required=True, help="Manifest Loom JSON")
    sealer.add_argument("--answers", type=Path, required=True, help="JSON answer array")
    sealer.add_argument("--operator-one", required=True)
    sealer.add_argument("--operator-two", required=True)
    sealer.add_argument("ledgers", nargs="+", type=Path)
    sealer.add_argument("--no-ledger", action="store_true")
    verifier = commands.add_parser("verify", help="verify sealed answers")
    verifier.add_argument("--report", type=Path, required=True)
    verifier.add_argument("ledgers", nargs="+", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    common = {
        "decision_key_one": os.environ.get("ALEPH_VERDICT_KEY_ONE"),
        "decision_key_two": os.environ.get("ALEPH_VERDICT_KEY_TWO"),
        "treaty_key_one": os.environ.get("ALEPH_TREATY_KEY_ONE"),
        "treaty_key_two": os.environ.get("ALEPH_TREATY_KEY_TWO"),
        "contract_key_one": os.environ.get("ALEPH_EXECUTOR_CONTRACT_KEY_ONE"),
        "contract_key_two": os.environ.get("ALEPH_EXECUTOR_CONTRACT_KEY_TWO"),
        "loom_key_one": os.environ.get("ALEPH_MANIFEST_LOOM_KEY_ONE"),
        "loom_key_two": os.environ.get("ALEPH_MANIFEST_LOOM_KEY_TWO"),
        "crucible_key_one": os.environ.get(KEY_ENV_ONE),
        "crucible_key_two": os.environ.get(KEY_ENV_TWO),
    }
    try:
        report = read_json(args.report, {})
        if not isinstance(report, dict):
            raise ValueError("report must contain a JSON object")
        if args.command == "seal":
            raw_answers = read_json(args.answers, [])
            if not isinstance(raw_answers, list):
                raise ValueError("answers must be a JSON array")
            result = seal_answers(
                report,
                answers=raw_answers,
                operator_one=args.operator_one,
                operator_two=args.operator_two,
                ledgers=args.ledgers,
                record=not args.no_ledger,
                **common,
            )
        else:
            valid = verify_sealed_answers(report, ledgers=args.ledgers, **common)
            result = {"ok": valid}
        json.dump(result, sys.stdout, sort_keys=True, indent=2)
        sys.stdout.write("\n")
        return 0 if args.command == "seal" or result["ok"] else 1
    except (OSError, TypeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
