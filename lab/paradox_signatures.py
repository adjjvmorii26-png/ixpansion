#!/usr/bin/env python3
"""Paradox Signature Database — fingerprint and classify anomaly patterns."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lab.runtime_vault import (
    append_jsonl,
    ledger_path,
    read_json,
    state_path,
    write_json,
)

SCHEMA = "aleph.experiments.paradox-signatures.v1"
FEATURE_DIMS = (
    "identity_collision",
    "state_fork",
    "clock_regression",
    "replay_echo",
    "broken_chain",
    "post_terminal",
    "energy_spike",
    "budget_exhaustion",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _hash(payload: dict[str, Any]) -> str:
    material = {k: v for k, v in payload.items() if k != "db_hash"}
    return hashlib.sha256(_canonical(material)).hexdigest()


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return round(dot / (norm_a * norm_b), 6)


def _fingerprint(paradox: dict[str, Any]) -> list[float]:
    """Derive a deterministic feature vector from paradox attributes."""
    features = []
    for dim in FEATURE_DIMS:
        val = float(paradox.get(dim, 0))
        features.append(val)
    risk = float(paradox.get("risk_index", 0))
    witnesses = len(paradox.get("witnesses", []))
    features.append(min(1.0, risk))
    features.append(min(1.0, witnesses / 10.0))
    return features


def _db_path() -> Path:
    return state_path("paradox", "signature_database.json")


def _load_db() -> dict[str, Any]:
    return read_json(_db_path(), {"signatures": {}, "schema_version": 1})


def _save_db(db: dict[str, Any]) -> None:
    write_json(_db_path(), db)


def ingest_paradox(
    paradox: dict[str, Any],
    *,
    label: str = "",
    clock: Any = utc_now,
) -> dict[str, Any]:
    """Ingest a paradox constellation and store its signature."""
    features = _fingerprint(paradox)
    sig_id = f"sig-{hashlib.sha256(_canonical({'features': features, 'label': label})).hexdigest()[:16]}"
    db = _load_db()
    entry = {
        "sig_id": sig_id,
        "label": label,
        "features": features,
        "dimensions": dict(zip(FEATURE_DIMS + ("risk_index", "witness_density"), features)),
        "ingested_at": clock(),
        "source_kind": paradox.get("kind", "unknown"),
    }
    db["signatures"][sig_id] = entry
    _save_db(db)
    return entry


def match_paradox(
    paradox: dict[str, Any],
    *,
    threshold: float = 0.7,
    clock: Any = utc_now,
) -> dict[str, Any]:
    """Find the closest known signature for a new paradox."""
    query_features = _fingerprint(paradox)
    db = _load_db()
    matches = []
    for sig_id, entry in db.get("signatures", {}).items():
        sim = _cosine_similarity(query_features, entry["features"])
        if sim >= threshold:
            matches.append({
                "sig_id": sig_id,
                "label": entry.get("label", ""),
                "similarity": sim,
                "source_kind": entry.get("source_kind", ""),
            })
    matches.sort(key=lambda m: m["similarity"], reverse=True)
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "experiment": "paradox-signatures",
        "status": "sealed",
        "mode": "read-only-classification",
        "sealed_at": clock(),
        "query_features": query_features,
        "threshold": threshold,
        "match_count": len(matches),
        "matches": matches[:5],
        "total_signatures": len(db.get("signatures", {})),
        "execution_enabled": False,
    }
    result["db_hash"] = _hash(result)
    return result


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    ing = sub.add_parser("ingest", help="ingest a paradox signature")
    ing.add_argument("--paradox", type=Path, required=True)
    ing.add_argument("--label", default="")
    mt = sub.add_parser("match", help="match a paradox against the database")
    mt.add_argument("--paradox", type=Path, required=True)
    mt.add_argument("--threshold", type=float, default=0.7)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        paradox = json.loads(Path(args.paradox).read_text())
        if args.command == "ingest":
            entry = ingest_paradox(paradox, label=args.label)
        else:
            entry = match_paradox(paradox, threshold=args.threshold)
        print(json.dumps(entry, sort_keys=True, indent=2))
        return 0
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
