#!/usr/bin/env python3
"""Translate sealed Chrono Forge mandates into Nexus-compatible resonance."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from typing import Any

from lab.runtime_vault import (
    ledger_path,
    read_json,
    read_jsonl,
    report_path,
    verify_jsonl,
    write_json,
)


SCHEMA = "aleph.bridge.mandate-resonance.v1"


def _canonical(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _hash(payload: Any) -> str:
    return hashlib.sha256(_canonical(payload)).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _mood(status: str, policy: str) -> str:
    if status == "rehearsed":
        return "dreaming"
    return {"ration": "conserving", "stabilize": "steady", "expand": "curious"}[policy]


def _verify_certificate(report: dict[str, Any]) -> bool:
    certificate = report.get("execution_certificate")
    if not certificate:
        return False
    body = {key: value for key, value in report.items() if key != "execution_certificate"}
    return _hash(body) == certificate


def _live_tick(report: dict[str, Any]) -> int:
    witnesses = report.get("witnesses", [])
    return int(witnesses[-1]["tick"]) if witnesses else -1


def _dream_tick(report: dict[str, Any]) -> int:
    start = int(report["oracle"]["signals"]["sandbox_ticks"])
    return start + int(report["planned_ticks"])


def resonate(
    mandate_report: dict[str, Any],
    *,
    clock=utc_now,
) -> dict[str, Any]:
    """Verify a mandate certificate and fold it into one portable pulse."""
    status = mandate_report.get("status")
    policy = mandate_report.get("chosen_policy")
    if status not in {"sealed", "rehearsed"}:
        raise ValueError("only sealed or rehearsed mandates may resonate")
    if policy not in {"ration", "stabilize", "expand"}:
        raise ValueError("unsupported mandate policy")
    if not isinstance(mandate_report.get("oracle"), dict):
        raise ValueError("portable mandate lacks its signed oracle")
    if not _verify_certificate(mandate_report):
        raise ValueError("mandate execution certificate is missing or modified")

    audit = verify_jsonl(ledger_path())
    if not audit.get("ok"):
        raise ValueError("proof ledger audit failed")
    expected_hashes = [item.get("entry_hash") for item in mandate_report.get("witnesses", [])]
    actual_by_hash = {
        record["entry_hash"]: record
        for record in read_jsonl(ledger_path())
        if record.get("type") == "mandate_tick"
        and record.get("parliament_hash") == mandate_report.get("parliament_hash")
    }
    if len(actual_by_hash) != len(expected_hashes):
        raise ValueError("mandate witness count disagrees with the proof ledger")
    for entry_hash, declared in zip(expected_hashes, mandate_report.get("witnesses", [])):
        record = actual_by_hash.get(entry_hash)
        if record is None:
            raise ValueError("declared witness is absent from the proof ledger")
        if record.get("tick") != declared.get("tick"):
            raise ValueError("witness tick disagrees with the mandate report")
        if record.get("after_hash") != declared.get("after_hash"):
            raise ValueError("witness state hash disagrees with the mandate report")

    budget = mandate_report.get(
        "final_entropy_budget",
        mandate_report.get("ghost_final_budget"),
    )
    witness_hashes = [item for item in expected_hashes if item]
    signature_material = {
        "certificate": mandate_report["execution_certificate"],
        "mode": status,
        "parliament_hash": mandate_report["parliament_hash"],
        "policy": policy,
        "planned_ticks": mandate_report["planned_ticks"],
        "witness_hashes": witness_hashes,
    }
    signature = _hash(signature_material)
    pulse = {
        "schema": SCHEMA,
        "bridge": "chrono-forge/nexus-observatory",
        "source_engine": "aleph.chronoforge.reversible-mandate",
        "mandate_status": status,
        "tick": _live_tick(mandate_report) if status == "sealed" else _dream_tick(mandate_report),
        "chaos": round(1.0 - float(budget), 5),
        "mood": _mood(status, policy),
        "regime": policy,
        "mesh_delivered": int(mandate_report["planned_ticks"]),
        "witnesses": len(witness_hashes),
        "signature": signature,
        "short_signature": signature[:16],
        "created_at": clock(),
    }
    return pulse


def publish(pulse: dict[str, Any], destination: Path | None = None) -> Path:
    target = destination or ROOT / "nexus_observatory" / "telemetry" / "resonance.jsonl.latest"
    line = json.dumps(pulse, sort_keys=True, separators=(",", ":")) + "\n"
    _atomic_text(Path(target), line)
    return Path(target)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=None, help="Reversible Mandate report")
    parser.add_argument("--destination", type=Path, default=None)
    parser.add_argument("--no-publish", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    source = args.report or report_path("reversible-mandate.json")
    try:
        pulse = resonate(read_json(source, {}))
        if not args.no_publish:
            pulse["published_to"] = str(publish(pulse, args.destination))
        print(json.dumps(pulse, sort_keys=True, indent=2))
        return 0
    except (KeyError, TypeError, ValueError) as error:
        failure = {"schema": SCHEMA, "ok": False, "error": str(error)}
        print(json.dumps(failure, sort_keys=True, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
