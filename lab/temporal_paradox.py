#!/usr/bin/env python3
"""Temporal Paradox Resolver — read-only forensic correlation of sealed ledgers."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import hashlib
import json
from collections import defaultdict
from typing import Any

from lab.runtime_vault import (
    CHAIN_FIELDS,
    append_jsonl,
    ledger_path,
    read_jsonl,
    report_path,
    verify_jsonl,
    write_json,
)


SCHEMA = "aleph.chronoforge.temporal-paradox.v1"
TERMINAL_STATES = {"archived", "fossilized", "retired", "sealed", "terminated"}


def _canonical(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _hash(payload: Any) -> str:
    return hashlib.sha256(_canonical(payload)).hexdigest()


def _public(record: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value for key, value in record.items()
        if key not in {*CHAIN_FIELDS, "ledger_entry_hash"}
    }


def _contradiction(kind: str, severity: str, rationale: str, **evidence: Any) -> dict[str, Any]:
    return {"kind": kind, "severity": severity, "rationale": rationale, "evidence": evidence}


def _default_ledgers() -> list[Path]:
    directory = ledger_path().parent
    return sorted(directory.glob("*.jsonl"))


def _scan(paths: list[Path]) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    paradoxes: list[dict[str, Any]] = []
    audits: dict[str, dict[str, Any]] = {}
    observations: list[tuple[int, int, Path, dict[str, Any]]] = []

    for path_index, path in enumerate(paths):
        audit = verify_jsonl(path)
        source = path.name
        audits[source] = audit
        records = read_jsonl(path)
        for ordinal, record in enumerate(records, 1):
            observations.append((path_index, ordinal, path, record))
        if not audit["ok"]:
            paradoxes.append(_contradiction(
                "broken_chain",
                "critical",
                "a ledger failed closed before semantic interpretation",
                ledger=source,
                failure=audit.get("failure"),
            ))

    event_bodies: dict[str, set[str]] = defaultdict(set)
    state_bodies: dict[tuple[str, Any], set[str]] = defaultdict(set)
    timelines: dict[str, list[tuple[int, int, Any]]] = defaultdict(list)

    for path_index, ordinal, path, record in observations:
        public = _public(record)
        source = path.name
        position = (path_index, ordinal)
        body_hash = _hash(public)
        event_id = record.get("event_id")
        subject_id = record.get("subject_id")
        status = str(record.get("status", "")).lower()

        if isinstance(event_id, str) and event_id:
            event_bodies[event_id].add(body_hash)

        tick = record.get("tick")
        if isinstance(subject_id, str) and subject_id and isinstance(tick, (int, float)):
            timeline_key = f"timeline:{subject_id}"
            timelines[timeline_key].append((path_index, ordinal, tick))
            history = sorted(timelines[timeline_key])
            prior = history[:-1]
            if prior and tick < max(item[2] for item in prior):
                paradoxes.append(_contradiction(
                    "causal_regression",
                    "major",
                    "a later observation returned to an earlier clock position",
                    subject_id=subject_id,
                    observed_tick=tick,
                    prior_tick=max(item[2] for item in prior),
                    ledger=source,
                ))

        state_hash = record.get("state_hash")
        if subject_id and tick is not None and state_hash:
            key = (str(subject_id), tick)
            state_bodies[key].add(str(state_hash))
            if len(state_bodies[key]) > 1:
                paradoxes.append(_contradiction(
                    "state_fork",
                    "critical",
                    "the same subject and clock collapsed into distinct states",
                    subject_id=subject_id,
                    tick=tick,
                    ledger=source,
                ))

        if subject_id and status in TERMINAL_STATES:
            later_activity = any(
                other_path != path
                or (other_index, other_ordinal) > position
                for other_index, other_ordinal, other_path, other in observations
                if other.get("subject_id") == subject_id
                and str(other.get("status", "")).lower() not in TERMINAL_STATES
                and (other_index, other_ordinal) > position
            )
            if later_activity:
                paradoxes.append(_contradiction(
                    "post_terminal_activity",
                    "critical",
                    "activity continued after a terminal lifecycle witness",
                    subject_id=subject_id,
                    terminal_status=status,
                    ledger=source,
                ))

    for event_id in sorted(event_bodies):
        occurrences = sum(
            1 for _, _, _, record in observations
            if record.get("event_id") == event_id
        )
        if len(event_bodies[event_id]) > 1:
            paradoxes.append(_contradiction(
                "identity_collision",
                "critical",
                "one event identifier carries incompatible histories",
                event_id=event_id,
                occurrence_count=occurrences,
            ))
        elif occurrences > 1:
            paradoxes.append(_contradiction(
                "replay_echo",
                "warning",
                "an identical event crossed more than one observation",
                event_id=event_id,
                occurrence_count=occurrences,
            ))

    return paradoxes, audits


def resolve(*, ledgers: list[Path] | None = None, record: bool = True) -> dict[str, Any]:
    """Correlate ledgers without changing their bytes or sequence."""
    paths = sorted({Path(item).resolve() for item in ledgers}) if ledgers is not None else _default_ledgers()
    raw_paradoxes, audits = _scan(paths)
    unique: dict[tuple[str, str, str], dict[str, Any]] = {}
    for item in raw_paradoxes:
        fingerprint = _hash(item)[:24]
        unique[(item["kind"], item["severity"], fingerprint)] = item
    paradoxes = sorted(
        unique.values(),
        key=lambda item: (
            {"critical": 0, "major": 1, "warning": 2}[item["severity"]],
            item["kind"],
            _canonical(item["evidence"]),
        ),
    )
    kinds = {item["kind"] for item in paradoxes}
    corrupt_count = sum(not audit["ok"] for audit in audits.values())
    verdict = "paradox" if corrupt_count or any(item["severity"] == "critical" for item in paradoxes) else (
        "unstable" if paradoxes else "coherent"
    )

    resolutions = []
    if "broken_chain" in kinds:
        resolutions.append("quarantine the affected ledger and restore from a checksummed backup")
    if "identity_collision" in kinds or "state_fork" in kinds:
        resolutions.append("split each fork behind a new nonce and preserve both witnesses")
    if "causal_regression" in kinds:
        resolutions.append("replay the subject through its last valid clock witness")
    if "post_terminal_activity" in kinds:
        resolutions.append("reopen the lifecycle only with explicit operator consent")
    if "replay_echo" in kinds and not resolutions:
        resolutions.append("retain replay evidence; no repair is required")
    if not resolutions:
        resolutions.append("preserve the coherent chain unchanged")

    result: dict[str, Any] = {
        "schema": SCHEMA,
        "experiment": "temporal-paradox-resolver",
        "status": "sealed",
        "mode": "read-only",
        "mutation_budget": 0,
        "verdict": verdict,
        "sources": {
            "ledger_count": len(paths),
            "audits": audits,
            "corrupt_ledger_count": corrupt_count,
        },
        "paradox_count": len(paradoxes),
        "paradoxes": paradoxes,
        "resolutions": resolutions,
        "guardrails": [
            "Source ledgers are opened read-only.",
            "The resolver never repairs evidence automatically.",
            "Critical contradictions fail closed without destructive cleanup.",
        ],
    }
    result["paradox_hash"] = _hash(result)

    if record:
        write_json(report_path("temporal-paradox.json"), result)
        sealed = append_jsonl(ledger_path("paradox-resolutions.jsonl"), result)
        result["ledger_entry_hash"] = sealed["entry_hash"]
        write_json(report_path("temporal-paradox.json"), result)
    return result


def resolver_is_sealed(report: dict[str, Any]) -> bool:
    if report.get("schema") != SCHEMA or report.get("status") != "sealed":
        return False
    claimed = report.get("paradox_hash")
    if not claimed:
        return False
    body = {
        key: value for key, value in report.items()
        if key not in {"paradox_hash", "ledger_entry_hash", *CHAIN_FIELDS}
    }
    return _hash(body) == claimed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledgers", nargs="*", type=Path, help="explicit JSONL ledgers to correlate")
    parser.add_argument("--no-ledger", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = resolve(ledgers=args.ledgers or None, record=not args.no_ledger)
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
