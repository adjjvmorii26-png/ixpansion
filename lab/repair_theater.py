#!/usr/bin/env python3
"""Ghost Repair Theater — rehearse recovery blueprints without execution authority."""
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

from lab.repair_dreams import DERIVED_LEDGERS, weave
from lab.runtime_vault import (
    CHAIN_FIELDS,
    append_jsonl,
    ledger_path,
    read_jsonl,
    report_path,
    verify_jsonl,
    write_json,
)


SCHEMA = "aleph.chronoforge.repair-theater.v1"
MAX_OPERATIONS_CEILING = 32


def _canonical(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _hash(payload: Any) -> str:
    return hashlib.sha256(_canonical(payload)).hexdigest()


def _clamp(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 5)


def _public(record: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value for key, value in record.items()
        if key not in {*CHAIN_FIELDS, "ledger_entry_hash"}
    }


def _paths(explicit: list[Path] | None) -> list[Path]:
    if explicit is None:
        directory = ledger_path().parent
        excluded = {*DERIVED_LEDGERS, "repair-theater.jsonl"}
        return sorted(path for path in directory.glob("*.jsonl") if path.name not in excluded)
    resolved = sorted({Path(item).resolve() for item in explicit})
    for item in resolved:
        if not item.is_file():
            raise ValueError(f"ledger does not exist: {item}")
    return resolved


def _observations(paths: list[Path]) -> list[dict[str, Any]]:
    rows = []
    for path in paths:
        for ordinal, record in enumerate(read_jsonl(path), 1):
            rows.append({
                "ledger": path.name,
                "ordinal": ordinal,
                "sequence": int(record.get("sequence", ordinal)),
                "record": record,
                "body_hash": _hash(_public(record)),
            })
    return sorted(rows, key=lambda row: (row["ledger"], row["sequence"], row["ordinal"]))


def _numeric(value: Any) -> float | None:
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def _branch(row: dict[str, Any], operation_id: str, label: str) -> dict[str, Any]:
    body = _public(row["record"])
    return {
        "branch_id": f"{operation_id}-{_hash(body)[:16]}",
        "label": label,
        "source_ledger": row["ledger"],
        "source_sequence": row["sequence"],
        "witness_hash": _hash(body),
        "ghost_event": body,
    }


def _state_fork_scenario(operation: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    blueprint = operation["blueprint"]
    subject = blueprint.get("target")
    tick = blueprint.get("tick")
    expected = set(operation["blueprint"].get("preserved_state_hashes", []))
    selected = [
        row for row in rows
        if row["record"].get("subject_id") == subject
        and row["record"].get("tick") == tick
        and str(row["record"].get("state_hash", "")) in expected
    ]
    branches = [
        _branch(row, operation["operation_id"], str(row["record"]["state_hash"])[:12])
        for row in selected
    ]
    preserved = len({item["witness_hash"] for item in branches})
    stability = 0.82 if len(expected) >= 2 and preserved == len(expected) else 0.18
    risks = [] if preserved == len(expected) else ["one or more conflicting witnesses was unreachable"]
    return {
        "status": "staged",
        "branches": branches,
        "stability": _clamp(stability),
        "residual_risks": risks,
    }


def _regression_scenario(operation: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    blueprint = operation["blueprint"]
    subject = blueprint.get("target")
    anchor_tick = _numeric(blueprint.get("anchor_tick"))
    quarantined_tick = _numeric(blueprint.get("quarantined_tick"))

    def tick(row: dict[str, Any]) -> float | None:
        return _numeric(row["record"].get("tick"))

    anchor_rows = [
        row for row in rows
        if row["record"].get("subject_id") == subject
        and tick(row) is not None
        and anchor_tick is not None
        and tick(row) == anchor_tick
    ]
    side_rows = [
        row for row in rows
        if row["record"].get("subject_id") == subject
        and tick(row) is not None
        and quarantined_tick is not None
        and tick(row) == quarantined_tick
    ]
    anchor = [_branch(row, operation["operation_id"], "anchor") for row in anchor_rows]
    side = [_branch(row, operation["operation_id"], "side-timeline") for row in side_rows]
    complete = bool(anchor and side)
    return {
        "status": "staged",
        "branches": [*anchor, *side],
        "stability": _clamp(0.78 if complete else 0.24),
        "residual_risks": [] if complete else ["rewind anchor or regressed timeline was unavailable"],
    }


def _collision_scenario(operation: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    event_id = operation["blueprint"].get("target")
    matches = [row for row in rows if row["record"].get("event_id") == event_id]
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in matches:
        groups.setdefault(row["body_hash"], []).append(row)
    branches = []
    for index, body_hash in enumerate(sorted(groups), 1):
        for row in groups[body_hash]:
            branches.append(_branch(row, operation["operation_id"], f"identity-{index}"))
    stable = len(groups) >= 2 and len(branches) == len(matches)
    return {
        "status": "staged",
        "branches": branches,
        "stability": _clamp(0.76 if stable else 0.20),
        "residual_risks": [] if stable else ["collision variants could not be partitioned cleanly"],
    }


def _replay_scenario(operation: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    event_id = operation["blueprint"].get("target")
    branches = [
        _branch(row, operation["operation_id"], "retained-echo")
        for row in rows if row["record"].get("event_id") == event_id
    ]
    return {
        "status": "retained",
        "branches": branches,
        "stability": _clamp(0.95 if branches else 0.10),
        "residual_risks": [],
    }


def _quarantine_scenario(operation: dict[str, Any], reason: str) -> dict[str, Any]:
    return {
        "status": "quarantined",
        "branches": [],
        "stability": _clamp(0.15),
        "residual_risks": [reason],
    }


def _rehearse(operation: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    kind = operation["kind"]
    if kind == "state_fork":
        scenario = _state_fork_scenario(operation, rows)
    elif kind == "causal_regression":
        scenario = _regression_scenario(operation, rows)
    elif kind == "identity_collision":
        scenario = _collision_scenario(operation, rows)
    elif kind == "replay_echo":
        scenario = _replay_scenario(operation, rows)
    elif kind == "broken_chain":
        scenario = _quarantine_scenario(operation, "broken chains cannot be safely staged")
    elif kind == "post_terminal_activity":
        scenario = _quarantine_scenario(operation, "lifecycle reopening requires human consent")
    else:
        scenario = {
            "status": "refused",
            "branches": [],
            "stability": 0.0,
            "residual_risks": ["unknown repair archetype"],
        }
    return {
        "operation_id": operation["operation_id"],
        "kind": kind,
        "action": operation["blueprint"]["action"],
        "consent_required": operation["consent_required"],
        "execution_enabled": False,
        "mutation_budget": 0,
        **scenario,
    }


def rehearse(*, ledgers: list[Path] | None = None, max_operations: int = 16, record: bool = True) -> dict[str, Any]:
    """Stage synthetic repair branches while forbidding all live mutation."""
    if not 1 <= max_operations <= MAX_OPERATIONS_CEILING:
        raise ValueError(f"max-operations must be between 1 and {MAX_OPERATIONS_CEILING}")
    paths = _paths(ledgers)
    if not paths:
        raise ValueError("no ledgers are available for ghost rehearsal")
    broken = [verify_jsonl(path) for path in paths]
    dream = weave(ledgers=paths, max_operations=max_operations, record=False)
    rows = _observations(paths)
    scenes = [_rehearse(operation, rows) for operation in dream["operations"]]
    statuses = {scene["status"] for scene in scenes}
    verdict = (
        "empty_stage" if not scenes else
        "fragmented_stage" if dream["truncated"] else
        "quarantined_stage" if "quarantined" in statuses or "refused" in statuses else
        "provenance_retained" if statuses == {"retained"} else
        "branches_staged"
    )
    average_stability = round(sum(scene["stability"] for scene in scenes) / len(scenes), 5) if scenes else 1.0

    result: dict[str, Any] = {
        "schema": SCHEMA,
        "experiment": "ghost-repair-theater",
        "status": "sealed",
        "mode": "synthetic-rehearsal",
        "verdict": verdict,
        "dream_hash": dream["dream_hash"],
        "source_audits_ok": all(audit["ok"] for audit in broken),
        "stage_count": len(scenes),
        "scenes": scenes,
        "branch_count": sum(len(scene["branches"]) for scene in scenes),
        "average_stability": average_stability,
        "execution_enabled": False,
        "live_mutation_budget": 0,
        "guardrails": [
            "Ghost events exist only inside this report.",
            "No source ledger is modified, reordered, deleted, or repaired.",
            "Every live action remains forbidden without separate human consent.",
        ],
    }
    result["theater_hash"] = _hash(result)

    if record:
        write_json(report_path("repair-theater.json"), result)
        sealed = append_jsonl(
            ledger_path("repair-theater.jsonl"),
            {key: value for key, value in result.items() if key != "ledger_entry_hash"},
        )
        result["ledger_entry_hash"] = sealed["entry_hash"]
        write_json(report_path("repair-theater.json"), result)
    return result


def theater_is_sealed(report: dict[str, Any]) -> bool:
    if report.get("schema") != SCHEMA or report.get("status") != "sealed":
        return False
    claimed = report.get("theater_hash")
    if not claimed:
        return False
    body = {
        key: value for key, value in report.items()
        if key not in {"theater_hash", "ledger_entry_hash", *CHAIN_FIELDS}
    }
    return _hash(body) == claimed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledgers", nargs="*", type=Path)
    parser.add_argument("--max-operations", type=int, default=16)
    parser.add_argument("--no-ledger", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = rehearse(
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
