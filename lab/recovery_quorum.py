#!/usr/bin/env python3
"""Recovery Quorum — convert safe ghost stages into non-executable consent packets."""
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

from lab.recovery_sources import source_ledgers
from lab.repair_theater import rehearse
from lab.runtime_vault import (
    CHAIN_FIELDS,
    append_jsonl,
    ledger_path,
    report_path,
    write_json,
)


SCHEMA = "aleph.chronoforge.recovery-quorum.v1"
MAX_OPERATIONS_CEILING = 32


def _canonical(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _hash(payload: Any) -> str:
    return hashlib.sha256(_canonical(payload)).hexdigest()


def _paths(explicit: list[Path] | None) -> list[Path]:
    return source_ledgers(explicit)


def _votes(scene: dict[str, Any], source_audits_ok: bool) -> dict[str, str]:
    residual = scene.get("residual_risks", [])
    branch_count = len(scene.get("branches", []))
    stability = float(scene.get("stability", 0.0))

    if scene["status"] in {"quarantined", "refused"} or residual or not source_audits_ok:
        archivist = "block"
    elif branch_count:
        archivist = "support"
    else:
        archivist = "review"

    unsafe_kind = scene["kind"] in {"broken_chain", "post_terminal_activity"}
    if not source_audits_ok or unsafe_kind or residual:
        sentinel = "block"
    elif scene["consent_required"]:
        sentinel = "review"
    else:
        sentinel = "support"

    if stability < 0.40:
        explorer = "block"
    elif stability >= 0.75 and branch_count >= 2:
        explorer = "support"
    else:
        explorer = "review"

    return {"archivist": archivist, "sentinel": sentinel, "explorer": explorer}


def _recommendation(scene: dict[str, Any], offices: dict[str, str]) -> tuple[str, bool]:
    blocks = sum(vote == "block" for vote in offices.values())
    supports = sum(vote == "support" for vote in offices.values())
    quorum_met = supports >= 2 and blocks == 0
    if blocks:
        return "human_tribunal", False
    if scene["status"] == "retained":
        return "preserve_provenance", False
    if quorum_met:
        return "prepare_consent_packet", True
    return "keep_ghost_only", False


def convene(
    *,
    ledgers: list[Path] | None = None,
    max_operations: int = 16,
    record: bool = True,
) -> dict[str, Any]:
    """Review ghost repairs and issue data-only consent packets when quorum agrees."""
    if not 1 <= max_operations <= MAX_OPERATIONS_CEILING:
        raise ValueError(f"max-operations must be between 1 and {MAX_OPERATIONS_CEILING}")
    paths = _paths(ledgers)
    if not paths:
        raise ValueError("no ledgers are available for recovery quorum")
    theater = rehearse(ledgers=paths, max_operations=max_operations, record=False)

    scenes = []
    packets = []
    for scene in theater["scenes"]:
        offices = _votes(scene, theater["source_audits_ok"])
        recommendation, packet_ready = _recommendation(scene, offices)
        reviewed = {
            **scene,
            "offices": offices,
            "supports": sum(vote == "support" for vote in offices.values()),
            "blocks": sum(vote == "block" for vote in offices.values()),
            "quorum_met": recommendation == "prepare_consent_packet",
            "recommendation": recommendation,
        }
        scenes.append(reviewed)
        if packet_ready:
            packets.append({
                "packet_id": f"consent-{_hash({'operation_id': scene['operation_id'], 'scene': scene})[:24]}",
                "operation_id": scene["operation_id"],
                "action": scene["action"],
                "scene_hash": _hash(scene),
                "offices": offices,
                "required_human_signatures": 2,
                "executable": False,
                "mutation_budget": 0,
                "expires_after_source_change": True,
            })

    blocked = any(item["blocks"] for item in scenes)
    retained_only = bool(scenes) and all(item["status"] == "retained" for item in scenes)
    verdict = (
        "dormant" if not scenes else
        "tribunal_required" if blocked else
        "provenance_preserved" if retained_only else
        "consent_ready" if packets else
        "ghost_only"
    )
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "experiment": "recovery-quorum",
        "status": "sealed",
        "mode": "advisory-consensus",
        "verdict": verdict,
        "theater_hash": theater["theater_hash"],
        "source_audits_ok": theater["source_audits_ok"],
        "scene_count": len(scenes),
        "scenes": scenes,
        "consent_packet_count": len(packets),
        "consent_packets": packets,
        "average_stability": theater["average_stability"],
        "execution_enabled": False,
        "live_mutation_budget": 0,
        "guardrails": [
            "Quorum approval creates a packet, never a live mutation.",
            "Blocked scenes require a human tribunal.",
            "Packets expire immediately when their source witness changes.",
        ],
    }
    result["quorum_hash"] = _hash(result)

    if record:
        write_json(report_path("recovery-quorum.json"), result)
        sealed = append_jsonl(
            ledger_path("recovery-quorums.jsonl"),
            {key: value for key, value in result.items() if key != "ledger_entry_hash"},
        )
        result["ledger_entry_hash"] = sealed["entry_hash"]
        write_json(report_path("recovery-quorum.json"), result)
    return result


def quorum_is_sealed(report: dict[str, Any]) -> bool:
    if report.get("schema") != SCHEMA or report.get("status") != "sealed":
        return False
    claimed = report.get("quorum_hash")
    if not claimed:
        return False
    body = {
        key: value for key, value in report.items()
        if key not in {"quorum_hash", "ledger_entry_hash", *CHAIN_FIELDS}
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
        result = convene(
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
