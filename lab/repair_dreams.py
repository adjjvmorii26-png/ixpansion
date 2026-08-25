#!/usr/bin/env python3
"""Repair Dream Weaver — turn paradox evidence into non-executable recovery dreams."""
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

from lab.recovery_sources import RECOVERY_DERIVED_LEDGERS as DERIVED_LEDGERS, source_ledgers
from lab.runtime_vault import (
    CHAIN_FIELDS,
    append_jsonl,
    ledger_path,
    report_path,
    verify_jsonl,
    write_json,
)
from lab.temporal_paradox import resolve


SCHEMA = "aleph.chronoforge.repair-dream.v1"
MAX_OPERATIONS_CEILING = 64
SEVERITY_WEIGHT = {"critical": 0.34, "major": 0.18, "warning": 0.07}


def _canonical(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _hash(payload: Any) -> str:
    return hashlib.sha256(_canonical(payload)).hexdigest()


def _source_ledgers(explicit: list[Path] | None) -> list[Path]:
    return source_ledgers(explicit)


def _state_hashes(evidence: dict[str, Any]) -> list[str]:
    witnesses = evidence.get("witnesses", [])
    values = []
    for witness in witnesses if isinstance(witnesses, list) else []:
        nested = witness.get("evidence", {})
        value = nested.get("state_hash") if isinstance(nested, dict) else None
        if isinstance(value, str):
            values.append(value)
    return sorted(set(values))


def _blueprint(kind: str, evidence: dict[str, Any], fingerprint: str) -> dict[str, Any]:
    if kind == "broken_chain":
        return {
            "action": "restore_from_checksummed_backup",
            "reason": "the source chain is untrustworthy until restored",
            "target": evidence.get("ledger"),
            "required_artifact": "checksummed backup",
        }
    if kind == "identity_collision":
        return {
            "action": "split_event_identity",
            "reason": "incompatible histories cannot share one identifier",
            "target": evidence.get("event_id"),
            "new_identity_suffix": fingerprint[:12],
        }
    if kind == "state_fork":
        return {
            "action": "branch_states",
            "reason": "each conflicting collapse deserves a preserved ghost branch",
            "target": evidence.get("subject_id"),
            "tick": evidence.get("tick"),
            "preserved_state_hashes": _state_hashes(evidence),
        }
    if kind == "causal_regression":
        return {
            "action": "rewind_to_anchor",
            "reason": "later observations must be rehearsed on a side timeline",
            "target": evidence.get("subject_id"),
            "anchor_tick": evidence.get("prior_tick"),
            "quarantined_tick": evidence.get("observed_tick"),
        }
    if kind == "post_terminal_activity":
        return {
            "action": "request_lifecycle_reopening",
            "reason": "terminal contradictions require explicit human consent",
            "target": evidence.get("subject_id"),
            "terminal_status": evidence.get("terminal_status"),
        }
    return {
        "action": "retain_replay_evidence",
        "reason": "identical repeats are useful provenance, not corruption",
        "target": evidence.get("event_id"),
    }


def _operation(paradox: dict[str, Any]) -> dict[str, Any]:
    evidence = paradox["evidence"]
    fingerprint = _hash({"kind": paradox["kind"], "evidence": evidence})
    return {
        "operation_id": f"dream-{fingerprint[:24]}",
        "kind": paradox["kind"],
        "severity": paradox["severity"],
        "consent_required": paradox["kind"] != "replay_echo",
        "executable": False,
        "mutation_budget": 0,
        "evidence_hash": _hash(evidence),
        "blueprint": _blueprint(paradox["kind"], evidence, fingerprint),
    }


def _verdict(operations: list[dict[str, Any]], truncated: bool) -> str:
    if truncated:
        return "fragmented"
    if any(item["severity"] == "critical" for item in operations):
        return "quarantined_dream"
    if any(item["severity"] == "major" for item in operations):
        return "healing_dream"
    if operations:
        return "provenance_dream"
    return "lucid"


def weave(
    *,
    ledgers: list[Path] | None = None,
    max_operations: int = 16,
    record: bool = True,
) -> dict[str, Any]:
    """Compile paradox diagnoses into data-only repair dreams without execution."""
    if not 1 <= max_operations <= MAX_OPERATIONS_CEILING:
        raise ValueError(f"max-operations must be between 1 and {MAX_OPERATIONS_CEILING}")

    paths = _source_ledgers(ledgers)
    if not paths:
        raise ValueError("no source ledgers are available to weave")
    for path in paths:
        audit = verify_jsonl(path)
        if not audit["ok"]:
            # Diagnosis still receives the failure so the dream can preserve it.
            continue

    diagnosis = resolve(ledgers=paths, record=False)
    all_operations = [_operation(item) for item in diagnosis["paradoxes"]]
    operations = all_operations[:max_operations]
    truncated = len(all_operations) > max_operations
    residual_warning_count = sum(item["kind"] == "replay_echo" for item in all_operations)
    projected_risk = round(min(1.0, residual_warning_count * SEVERITY_WEIGHT["warning"]), 5)

    result: dict[str, Any] = {
        "schema": SCHEMA,
        "experiment": "repair-dream-weaver",
        "status": "sealed",
        "mode": "data-only",
        "mutation_budget": 0,
        "execution_enabled": False,
        "verdict": _verdict(all_operations, truncated),
        "diagnosis_hash": diagnosis["paradox_hash"],
        "risk_before": diagnosis["risk"],
        "projected_risk_after_human_execution": {
            "index": projected_risk,
            "retained_replay_warnings": residual_warning_count,
        },
        "operation_count": len(operations),
        "operations": operations,
        "truncated": truncated,
        "guardrails": [
            "Dreams never touch the source ledgers.",
            "Every mutating blueprint requires explicit operator consent.",
            "The engine has zero execution authority.",
        ],
    }
    result["dream_hash"] = _hash(result)

    if record:
        write_json(report_path("repair-dreams.json"), result)
        sealed = append_jsonl(
            ledger_path("repair-dreams.jsonl"),
            {key: value for key, value in result.items() if key != "ledger_entry_hash"},
        )
        result["ledger_entry_hash"] = sealed["entry_hash"]
        write_json(report_path("repair-dreams.json"), result)
    return result


def dream_is_sealed(report: dict[str, Any]) -> bool:
    if report.get("schema") != SCHEMA or report.get("status") != "sealed":
        return False
    claimed = report.get("dream_hash")
    if not claimed:
        return False
    body = {
        key: value for key, value in report.items()
        if key not in {"dream_hash", "ledger_entry_hash", *CHAIN_FIELDS}
    }
    return _hash(body) == claimed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledgers", nargs="*", type=Path, help="explicit JSONL ledgers to diagnose")
    parser.add_argument("--max-operations", type=int, default=16)
    parser.add_argument("--no-ledger", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = weave(
            ledgers=args.ledgers or None,
            max_operations=args.max_operations,
            record=not args.no_ledger,
        )
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (OSError, TypeError, ValueError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, sort_keys=True, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
