#!/usr/bin/env python3
"""Recovery Manifest Loom — seal human recovery intents without execution rights."""
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

from lab.recovery_shadow_red_cell import SCHEMA as SHADOW_SCHEMA, verify_shadow_cell
from lab.runtime_vault import (
    CHAIN_FIELDS,
    append_jsonl,
    ledger_path,
    read_json,
    read_jsonl,
    report_path,
    write_json,
)


SCHEMA = "aleph.chronoforge.recovery-manifest-loom.v1"
MIN_KEY_LENGTH = 16
KEY_ENV_ONE = "ALEPH_MANIFEST_LOOM_KEY_ONE"
KEY_ENV_TWO = "ALEPH_MANIFEST_LOOM_KEY_TWO"
INTENT_KINDS = {
    "observe": "inspect evidence without changing it",
    "preserve": "create an additional offline human-held witness",
    "prepare_review": "organize material for independent human review",
}
MAX_THREADS = 7


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _hash(payload: dict[str, Any]) -> str:
    material = {key: value for key, value in payload.items() if key != "loom_hash"}
    return hashlib.sha256(_canonical(material)).hexdigest()


def _key(value: str | None, environment_name: str) -> bytes:
    encoded = (value or os.environ.get(environment_name, "")).encode("utf-8")
    if len(encoded) < MIN_KEY_LENGTH:
        raise ValueError(f"{environment_name} must contain at least {MIN_KEY_LENGTH} bytes")
    return encoded


def _fingerprint(key: bytes) -> str:
    return hmac.new(key, b"aleph.recovery-manifest-loom.key-fingerprint.v1", hashlib.sha256).hexdigest()


def _slug(value: str) -> bool:
    return bool(value) and value == value.lower().replace("_", "-") and all(
        character.isalnum() or character == "-" for character in value
    )


def _validate_threads(raw: Any, witnesses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(raw, list) or not 1 <= len(raw) <= MAX_THREADS:
        raise ValueError(f"a manifest requires 1 to {MAX_THREADS} intent threads")
    allowed_targets = sorted({item["ledger"] for item in witnesses})
    seen: set[str] = set()
    validated = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"intent thread {index + 1} must be an object")
        required = {
            "thread_id",
            "kind",
            "title",
            "rationale",
            "bound_ledger",
        }
        if set(item) != required:
            raise ValueError(f"intent thread {index + 1} must contain exactly {sorted(required)}")
        thread_id = str(item["thread_id"])
        kind = str(item["kind"])
        title = str(item["title"]).strip()
        rationale = " ".join(str(item["rationale"]).split())
        bound_ledger = str(item["bound_ledger"])
        if not _slug(thread_id) or len(thread_id) > 60:
            raise ValueError(f"intent thread {index + 1} needs a lowercase slug id of 60 characters or fewer")
        if thread_id in seen:
            raise ValueError(f"duplicate intent thread id: {thread_id}")
        if kind not in INTENT_KINDS:
            raise ValueError(f"unsupported intent kind: {kind}")
        if not 12 <= len(title) <= 160:
            raise ValueError(f"intent thread {thread_id} title must contain 12 to 160 characters")
        if len(rationale) < 40:
            raise ValueError(f"intent thread {thread_id} rationale is too short for human review")
        if bound_ledger not in allowed_targets:
            raise ValueError(
                f"intent thread {thread_id} must bind one reviewed ledger: {', '.join(allowed_targets)}"
            )
        seen.add(thread_id)
        validated.append({
            "thread_id": thread_id,
            "kind": kind,
            "title": title,
            "rationale": rationale,
            "bound_ledger": bound_ledger,
            "permitted_effect": INTENT_KINDS[kind],
            "mutation_enabled": False,
        })
    return validated


def _lenses(thread: dict[str, Any]) -> list[dict[str, str]]:
    """Generate review lenses; they ask questions rather than encode actions."""
    ident = thread["thread_id"]
    target = thread["bound_ledger"]
    return [
        {
            "lens": "provenance",
            "inquiry": f"Which immutable bytes in {target} prove the condition described by {ident}?",
            "status": "awaiting_independent_human_answer",
        },
        {
            "lens": "consequence",
            "inquiry": f"What observable evidence would reveal that {ident} affected anything beyond its declared intent?",
            "status": "awaiting_independent_human_answer",
        },
        {
            "lens": "reversibility",
            "inquiry": f"How can a human preserve or restore the pre-review state around {target} without automation?",
            "status": "awaiting_independent_human_answer",
        },
    ]


def _core(
    shadow: dict[str, Any],
    *,
    threads: list[dict[str, Any]],
    operators: list[str],
    nonce: str,
    woven_at: str,
) -> dict[str, Any]:
    contract = shadow["source_contract"]
    proposal = contract["proposal"]
    manifest_id_seed = {
        "shadow_hash": shadow["red_cell_hash"],
        "threads": threads,
        "operators": operators,
        "nonce": nonce,
    }
    return {
        "schema": SCHEMA,
        "experiment": "recovery-manifest-loom",
        "status": "sealed_for_human_manifest_review",
        "mode": "zero-authority-intent-weaving",
        "disposition": "ready_for_independent_human_answers",
        "woven_at": woven_at,
        "nonce": nonce,
        "source_shadow": shadow,
        "manifest_id": f"manifest-{_hash(manifest_id_seed)[:24]}",
        "operators": operators,
        "shadow_hash": shadow["red_cell_hash"],
        "contract_hash": contract["contract_hash"],
        "verdict_hash": proposal["verdict_hash"],
        "lineage_parameters": dict(proposal["lineage_parameters"]),
        "bound_witnesses": list(proposal["source_witnesses"]),
        "threads": [
            {**thread, "review_lenses": _lenses(thread)}
            for thread in threads
        ],
        "authority": {
            "execution_enabled": False,
            "live_mutation_budget": 0,
            "compatible_executors": [],
            "human_answers_required": len(threads) * 3,
            "next_permitted_action": "collect_independent_human_lens_answers_offline",
        },
        "guardrails": [
            "Intent threads are structured questions, never executable instructions.",
            "Only observe, preserve, and prepare-review effects are expressible.",
            "No lens answer can transform this artifact into an executor.",
        ],
    }


def _already_recorded(manifest_id: str) -> bool:
    ledger = ledger_path("recovery-manifest-looms.jsonl")
    return any(record.get("manifest_id") == manifest_id for record in read_jsonl(ledger))


def weave_manifest(
    shadow: dict[str, Any],
    *,
    intents: list[dict[str, Any]],
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
    clock: Callable[[], str] = utc_now,
    nonce: str | None = None,
    record: bool = True,
) -> dict[str, Any]:
    """Bind independently signed human intents to a verified shadow-reviewed contract."""
    if shadow.get("schema") != SHADOW_SCHEMA or shadow.get("disposition") != "ready_for_separate_human_manifest_review":
        raise ValueError("a verified shadow red-cell report is required")

    if not verify_shadow_cell(
        shadow,
        ledgers=ledgers,
        decision_key_one=decision_key_one,
        decision_key_two=decision_key_two,
        treaty_key_one=treaty_key_one,
        treaty_key_two=treaty_key_two,
        contract_key_one=contract_key_one,
        contract_key_two=contract_key_two,
    ):
        raise ValueError("shadow red-cell review is invalid or its witnesses changed")

    labels = [operator_one.strip()[:100], operator_two.strip()[:100]]
    if not all(labels) or labels[0] == labels[1]:
        raise ValueError("two distinct human operator labels are required")

    first_key = _key(loom_key_one, KEY_ENV_ONE)
    second_key = _key(loom_key_two, KEY_ENV_TWO)
    fingerprints = [_fingerprint(first_key), _fingerprint(second_key)]
    if hmac.compare_digest(*fingerprints):
        raise ValueError("manifest loom keys must be independent")

    threads = _validate_threads(intents, shadow["source_contract"]["proposal"]["source_witnesses"])
    selected_nonce = nonce or secrets.token_hex(16)
    core = _core(
        shadow,
        threads=threads,
        operators=labels,
        nonce=selected_nonce,
        woven_at=clock(),
    )
    signatures = []
    keys = (first_key, second_key)
    roles = ("author_one", "author_two")
    for role, operator_index in zip(roles, (0, 1)):
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

    if record and _already_recorded(core["manifest_id"]):
        raise ValueError("manifest has already been recorded by the loom")
    core["loom_hash"] = _hash(core)

    if record:
        write_json(report_path("recovery-manifest-loom.json"), core)
        sealed = append_jsonl(
            ledger_path("recovery-manifest-looms.jsonl"),
            {key: value for key, value in core.items() if key != "ledger_entry_hash"},
        )
        core["ledger_entry_hash"] = sealed["entry_hash"]
        write_json(report_path("recovery-manifest-loom.json"), core)
    return core


def verify_weave(
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
) -> bool:
    """Verify both authors, the full upstream chain, and every sealed intent lens."""
    if report.get("schema") != SCHEMA or report.get("status") != "sealed_for_human_manifest_review":
        return False
    claimed = report.get("loom_hash")
    authorization = report.get("authorization", {})
    if not claimed or authorization.get("signature_count") != 2:
        return False
    if authorization.get("execution_enabled") is not False:
        return False
    if authorization.get("compatible_executors") != []:
        return False
    body = {
        key: value for key, value in report.items()
        if key not in {"loom_hash", "ledger_entry_hash", *CHAIN_FIELDS}
    }
    if _hash(body) != claimed:
        return False

    shadow = report.get("source_shadow")
    if not isinstance(shadow, dict):
        return False

    # The portable report carries the upstream review so verification remains offline.
    if not verify_shadow_cell(
        shadow,
        ledgers=ledgers,
        decision_key_one=decision_key_one,
        decision_key_two=decision_key_two,
        treaty_key_one=treaty_key_one,
        treaty_key_two=treaty_key_two,
        contract_key_one=contract_key_one,
        contract_key_two=contract_key_two,
    ):
        return False
    if shadow.get("red_cell_hash") != report.get("shadow_hash"):
        return False

    try:
        expected_core = _core(
            shadow,
            threads=[{key: value for key, value in thread.items() if key != "review_lenses"} for thread in report.get("threads", [])],
            operators=list(report.get("operators", [])),
            nonce=str(report.get("nonce", "")),
            woven_at=str(report.get("woven_at", "")),
        )
    except (KeyError, TypeError, ValueError):
        return False
    unsigned_body = {key: value for key, value in body.items() if key != "authorization"}
    if unsigned_body != expected_core:
        return False

    signatures = {item.get("role"): item for item in authorization.get("signatures", [])}
    if set(signatures) != {"author_one", "author_two"}:
        return False
    keys = (_key(loom_key_one, KEY_ENV_ONE), _key(loom_key_two, KEY_ENV_TWO))
    fingerprints = [_fingerprint(keys[0]), _fingerprint(keys[1])]
    if hmac.compare_digest(*fingerprints):
        return False
    unsigned_body = {key: value for key, value in body.items() if key != "authorization"}
    for role, key, fingerprint in zip(("author_one", "author_two"), keys, fingerprints):
        stored = signatures[role]
        expected = hmac.new(key, _canonical(unsigned_body), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(stored.get("signature", ""), expected):
            return False
        if not hmac.compare_digest(stored.get("key_fingerprint", ""), fingerprint):
            return False
        if stored.get("operator_label") not in report.get("operators", []):
            return False
    return True


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    weaver = commands.add_parser("weave", help="seal structured human recovery intents")
    weaver.add_argument("--report", type=Path, required=True, help="shadow red-cell JSON")
    weaver.add_argument("--intents", type=Path, required=True, help="JSON array of intent threads")
    weaver.add_argument("--operator-one", required=True)
    weaver.add_argument("--operator-two", required=True)
    weaver.add_argument("ledgers", nargs="+", type=Path)
    weaver.add_argument("--no-ledger", action="store_true")
    verifier = commands.add_parser("verify", help="verify a woven manifest")
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
        "loom_key_one": os.environ.get(KEY_ENV_ONE),
        "loom_key_two": os.environ.get(KEY_ENV_TWO),
    }
    try:
        report = read_json(args.report, {})
        if not isinstance(report, dict):
            raise ValueError("report must contain a JSON object")
        if args.command == "weave":
            raw_intents = read_json(args.intents, [])
            if not isinstance(raw_intents, list):
                raise ValueError("intents must be a JSON array")
            result = weave_manifest(
                report,
                intents=raw_intents,
                operator_one=args.operator_one,
                operator_two=args.operator_two,
                ledgers=args.ledgers,
                record=not args.no_ledger,
                **common,
            )
        else:
            valid = verify_weave(report, ledgers=args.ledgers, **common)
            result = {"ok": valid}
        json.dump(result, sys.stdout, sort_keys=True, indent=2)
        sys.stdout.write("\n")
        return 0 if args.command == "weave" or result["ok"] else 1
    except (OSError, TypeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
