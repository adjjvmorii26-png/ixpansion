#!/usr/bin/env python3
"""Recovery Treaty Compiler — dual-key authorization without execution authority."""
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

from lab.recovery_atlas import compile_atlas
from lab.runtime_vault import (
    CHAIN_FIELDS,
    append_jsonl,
    ledger_path,
    read_json,
    read_jsonl,
    report_path,
    write_json,
)


SCHEMA = "aleph.chronoforge.recovery-treaty.v1"
MIN_KEY_LENGTH = 16
KEY_ENV_ONE = "ALEPH_TREATY_KEY_ONE"
KEY_ENV_TWO = "ALEPH_TREATY_KEY_TWO"


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
    return hmac.new(key, b"aleph.recovery-treaty.key-fingerprint.v1", hashlib.sha256).hexdigest()


def _source_binding(paths: list[Path]) -> list[dict[str, Any]]:
    return [
        {
            "ledger": path.name,
            "bytes_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "record_count": len(read_jsonl(path)),
        }
        for path in paths
    ]


def _selected_packet(atlas: dict[str, Any], packet_id: str | None) -> tuple[dict[str, Any], dict[str, Any]]:
    packets = atlas["journey"]["quorum"]["consent_packets"]
    scenes = atlas["journey"]["quorum"]["scenes"]
    matches = [item for item in packets if not packet_id or item.get("packet_id") == packet_id]
    if len(matches) != 1:
        raise ValueError("approved recovery packet is absent, blocked, or ambiguous")
    packet = matches[0]
    scene_matches = [item for item in scenes if item.get("operation_id") == packet.get("operation_id")]
    if len(scene_matches) != 1:
        raise ValueError("recovery packet has no unique ghost-stage witness")
    scene = scene_matches[0]
    if not atlas["source_audits_ok"] or scene.get("blocks"):
        raise ValueError("blocked or corrupt recovery evidence cannot be signed")
    if packet.get("executable") is not False or packet.get("mutation_budget") != 0:
        raise ValueError("refusing a treaty packet that carries mutation authority")
    return packet, scene


def _grant_material(
    *,
    packet: dict[str, Any],
    scene: dict[str, Any],
    binding: dict[str, Any],
    nonce: str,
    operators: list[str],
) -> dict[str, Any]:
    return {
        "context": "aleph.recovery-treaty.authorization.v1",
        "action": packet["action"],
        "operation_id": packet["operation_id"],
        "packet_id": packet["packet_id"],
        "scene_hash": _hash(scene),
        "upstream_hashes": binding["upstream_hashes"],
        "sources": binding["sources"],
        "nonce": nonce,
        "operators": operators,
    }


def compile_treaty(
    *,
    ledgers: list[Path] | None = None,
    packet_id: str | None = None,
    operator_one: str,
    operator_two: str,
    max_operations: int = 16,
    clock=utc_now,
    nonce: str | None = None,
    key_one: str | None = None,
    key_two: str | None = None,
    record: bool = True,
) -> dict[str, Any]:
    """Bind a quorum-approved packet to immutable witnesses under two independent keys."""
    labels = [operator_one.strip()[:100], operator_two.strip()[:100]]
    if not all(labels) or labels[0] == labels[1]:
        raise ValueError("two distinct operator labels are required")

    first_key = _key(key_one, KEY_ENV_ONE)
    second_key = _key(key_two, KEY_ENV_TWO)
    first_fp = _fingerprint(first_key)
    second_fp = _fingerprint(second_key)
    if hmac.compare_digest(first_fp, second_fp):
        raise ValueError("treaty keys must be independent")

    atlas = compile_atlas(
        ledgers=ledgers,
        max_operations=max_operations,
        record=False,
    )
    if atlas["verdict"] != "consent_ready":
        raise ValueError("recovery journey is not in consent_ready state")
    packet, scene = _selected_packet(atlas, packet_id)
    paths = sorted({Path(item) for item in ledgers}) if ledgers is not None else []
    upstream_hashes = {name: item["hash"] for name, item in atlas["upstream"].items()}
    binding = {
        "atlas_hash": atlas["atlas_hash"],
        "upstream_hashes": upstream_hashes,
        "sources": _source_binding(paths) if paths else atlas["sources"],
        "lineage_parameters": {
            "max_operations": max_operations,
        },
    }
    grant = _grant_material(
        packet=packet,
        scene=scene,
        binding=binding,
        nonce=nonce or secrets.token_hex(16),
        operators=labels,
    )
    signatures = []
    for role, key, fingerprint in (
        ("steward_one", first_key, first_fp),
        ("steward_two", second_key, second_fp),
    ):
        signatures.append({
            "role": role,
            "operator_label": labels[0 if role == "steward_one" else 1],
            "key_fingerprint": fingerprint,
            "signature": hmac.new(key, _canonical(grant), hashlib.sha256).hexdigest(),
        })

    result: dict[str, Any] = {
        "schema": SCHEMA,
        "experiment": "recovery-treaty",
        "status": "authorized_for_human_tribunal",
        "treaty_id": f"treaty-{_hash({'packet': packet, 'binding': binding, 'nonce': grant['nonce']})[:24]}",
        "signed_at": clock(),
        "nonce": grant["nonce"],
        "operators": labels,
        "packet": packet,
        "scene_witness_hash": grant["scene_hash"],
        "binding": binding,
        "authorization": {
            "required_signatures": 2,
            "signature_count": 2,
            "signatures": signatures,
            "granted_authority": "present_to_human_tribunal",
            "execution_enabled": False,
            "live_mutation_budget": 0,
        },
        "guardrails": [
            "Signing never executes or authorizes automated mutation.",
            "Raw keys exist only in their out-of-band environment.",
            "Any byte change in a bound source voids the treaty.",
        ],
    }
    result["treaty_hash"] = _hash(result)

    if record:
        write_json(report_path("recovery-treaty.json"), result)
        sealed = append_jsonl(
            ledger_path("recovery-treaties.jsonl"),
            {key: value for key, value in result.items() if key != "ledger_entry_hash"},
        )
        result["ledger_entry_hash"] = sealed["entry_hash"]
        write_json(report_path("recovery-treaty.json"), result)
    return result


def verify_treaty(
    report: dict[str, Any],
    *,
    ledgers: list[Path] | None = None,
    key_one: str | None = None,
    key_two: str | None = None,
    max_operations: int | None = None,
) -> bool:
    """Verify both signatures and confirm every bound witness remains unchanged."""
    if report.get("schema") != SCHEMA or report.get("status") != "authorized_for_human_tribunal":
        return False
    claimed = report.get("treaty_hash")
    auth = report.get("authorization", {})
    if not claimed or auth.get("signature_count") != 2 or auth.get("execution_enabled") is not False:
        return False
    body = {
        key: value for key, value in report.items()
        if key not in {"treaty_hash", "ledger_entry_hash", *CHAIN_FIELDS}
    }
    if _hash(body) != claimed:
        return False

    binding = report["binding"]
    bound_parameters = binding.get("lineage_parameters", {})
    bound_max_operations = bound_parameters.get("max_operations", 16)
    if max_operations is not None and max_operations != bound_max_operations:
        return False

    atlas = compile_atlas(ledgers=ledgers, max_operations=bound_max_operations, record=False)
    current_hashes = {name: item["hash"] for name, item in atlas["upstream"].items()}
    current_sources = _source_binding(sorted({Path(item) for item in ledgers})) if ledgers else atlas["sources"]
    if binding["atlas_hash"] != atlas["atlas_hash"]:
        return False
    if binding["upstream_hashes"] != current_hashes or binding["sources"] != current_sources:
        return False

    packet, scene = _selected_packet(atlas, report["packet"].get("packet_id"))
    if packet != report["packet"] or _hash(scene) != report["scene_witness_hash"]:
        return False

    grant = _grant_material(
        packet=packet,
        scene=scene,
        binding=binding,
        nonce=report["nonce"],
        operators=report["operators"],
    )
    signatures = {item["role"]: item for item in auth["signatures"]}
    expected_roles = {"steward_one", "steward_two"}
    if set(signatures) != expected_roles:
        return False
    keys = (_key(key_one, KEY_ENV_ONE), _key(key_two, KEY_ENV_TWO))
    fingerprints = [_fingerprint(key) for key in keys]
    if hmac.compare_digest(fingerprints[0], fingerprints[1]):
        return False
    for role, key in zip(("steward_one", "steward_two"), keys):
        stored = signatures[role]
        expected = hmac.new(key, _canonical(grant), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(stored["signature"], expected):
            return False
        if not hmac.compare_digest(stored["key_fingerprint"], _fingerprint(key)):
            return False
    return True


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    signer = commands.add_parser("sign", help="sign one consent-ready recovery packet")
    signer.add_argument("ledgers", nargs="*", type=Path)
    signer.add_argument("--packet-id", default=None)
    signer.add_argument("--operator-one", required=True)
    signer.add_argument("--operator-two", required=True)
    signer.add_argument("--max-operations", type=int, default=16)
    signer.add_argument("--no-ledger", action="store_true")
    verifier = commands.add_parser("verify", help="verify a treaty against unchanged sources")
    verifier.add_argument("ledgers", nargs="*", type=Path)
    verifier.add_argument("--report", type=Path, default=None)
    verifier.add_argument("--max-operations", type=int, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "sign":
            result = compile_treaty(
                ledgers=args.ledgers or None,
                packet_id=args.packet_id,
                operator_one=args.operator_one,
                operator_two=args.operator_two,
                max_operations=args.max_operations,
                record=not args.no_ledger,
            )
        else:
            report = read_json(args.report or report_path("recovery-treaty.json"), {})
            valid = verify_treaty(
                report,
                ledgers=args.ledgers or None,
                max_operations=args.max_operations,
            )
            result = {"ok": valid, "treaty_hash": report.get("treaty_hash")}
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (OSError, TypeError, ValueError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, sort_keys=True, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
