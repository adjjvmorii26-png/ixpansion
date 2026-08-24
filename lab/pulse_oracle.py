#!/usr/bin/env python3
"""Pulse Oracle — deterministic entropy forecasts from witnessed Chrono Forge state."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import hashlib
import json
import math
from typing import Any

from lab.runtime_vault import (
    append_jsonl,
    ledger_path,
    read_json,
    read_jsonl,
    report_path,
    state_path,
    verify_jsonl,
    write_json,
)


SCHEMA = "aleph.chronoforge.pulse-oracle.v1"


def _canonical(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _signal(tick: int, phase: float) -> tuple[float, float]:
    alpha = math.sin(2 * math.pi * 0.7 * tick * 0.1 + phase)
    beta = math.sin(2 * math.pi * 1.3 * tick * 0.1 + phase * 0.5)
    return round(alpha, 5), round(beta, 5)


def _verdict(entropy_budget: float, average_energy: float) -> tuple[str, list[str]]:
    if entropy_budget < 0.20:
        return "ration", [
            {"ritual": "entropy_fast", "reason": "projected reserve approaches the hard floor"},
            {"ritual": "shadow_replay", "reason": "prove the next mutation without spending live budget"},
        ]
    if average_energy > 0.62 or entropy_budget < 0.45:
        return "stabilize", [
            {"ritual": "phase_dampening", "reason": "recent signal energy is above the stable band"},
            {"ritual": "witness_audit", "reason": "preserve a rollback witness before further ticks"},
        ]
    return "expand", [
        {"ritual": "bounded_growth", "reason": "entropy and energy have room for a reversible expansion"},
        {"ritual": "proof_seal", "reason": "convert the favorable window into chained evidence"},
    ]


def forecast(
    *,
    sandbox_state: dict[str, Any],
    pulse_state: dict[str, Any],
    flux_state: dict[str, Any],
    ledger_records: list[dict[str, Any]],
    audit: dict[str, Any],
    horizon: int = 7,
) -> dict[str, Any]:
    """Project future sandbox pressure without mutating any world state."""
    if horizon < 1 or horizon > 30:
        raise ValueError("horizon must be between 1 and 30")
    history = [item for item in sandbox_state.get("history", []) if isinstance(item, dict)]
    recent_energy = [float(item.get("energy") or 0) for item in history[-7:]]
    average_energy = round(sum(recent_energy) / max(len(recent_energy), 1), 5)
    entropy_budget = round(float(sandbox_state.get("entropy_budget") or 1), 5)
    novelty = round(float(sandbox_state.get("novelty") or 0), 5)
    tick = int(sandbox_state.get("ticks") or 0)
    phase = float(sandbox_state.get("phase") or 0)

    projected_budget = entropy_budget
    projections = []
    forecast_phase = phase
    for offset in range(1, horizon + 1):
        alpha, beta = _signal(tick + offset, forecast_phase)
        energy = round(0.5 * (alpha * alpha + beta * beta), 5)
        projected_budget = max(0.05, projected_budget - 0.01 * energy)
        forecast_phase = (forecast_phase + 0.17 + 0.05 * alpha) % (2 * math.pi)
        projections.append({
            "offset": offset, "tick": tick + offset, "energy": energy,
            "entropy_budget": round(projected_budget, 5),
        })

    verdict, recommendations = _verdict(projected_budget, average_energy)
    evidence_count = len(ledger_records)
    confidence = round(min(0.99, 0.42 + min(evidence_count, 20) * 0.02 + min(len(history), 20) * 0.01), 4)
    model = {
        "schema": SCHEMA,
        "experiment": "pulse-oracle",
        "verdict": verdict,
        "confidence": confidence,
        "signals": {
            "entropy_budget": entropy_budget,
            "average_recent_energy": average_energy,
            "novelty": novelty,
            "sandbox_ticks": tick,
            "pulse_beats": int(pulse_state.get("beats") or 0),
            "pulse_phase": round(float(pulse_state.get("phase") or 0), 6),
            "flux_generation": int(flux_state.get("gen") or 0),
            "ledger_records": evidence_count,
            "ledger_tail_hash": audit.get("tail_hash", ""),
        },
        "audit": {"ok": audit.get("ok"), "chained_records": audit.get("chained_records", 0)},
        "forecast": {
            "horizon": horizon,
            "projected_entropy_budget": projections[-1]["entropy_budget"],
            "peak_energy": max(item["energy"] for item in projections),
            "projections": projections,
        },
        "recommendations": recommendations,
    }
    model["oracle_hash"] = hashlib.sha256(_canonical(model)).hexdigest()
    return model


def collect() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    audit = verify_jsonl(ledger_path())
    records = read_jsonl(ledger_path())
    return (
        read_json(state_path("sandbox", "engine.json"), {}),
        read_json(state_path("pulse", "state.json"), {}),
        read_json(state_path("worlds", "flux.json"), {}),
        records,
        audit,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--horizon", type=int, default=7)
    parser.add_argument("--no-ledger", action="store_true", help="do not append an oracle observation")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    sandbox_state, pulse_state, flux_state, records, audit = collect()
    result = forecast(
        sandbox_state=sandbox_state,
        pulse_state=pulse_state,
        flux_state=flux_state,
        ledger_records=records,
        audit=audit,
        horizon=args.horizon,
    )
    if not audit.get("ok"):
        result["status"] = "refused"
        result["refusal"] = "ledger audit failed"
        result.pop("oracle_hash", None)
        write_json(report_path("pulse-oracle.json"), result)
        print(json.dumps(result, sort_keys=True, indent=2))
        return 1
    result["status"] = "sealed"
    write_json(report_path("pulse-oracle.json"), result)
    if not args.no_ledger:
        append_jsonl(ledger_path(), {
            "type": "pulse_oracle",
            "verdict": result["verdict"],
            "oracle_hash": result["oracle_hash"],
            "horizon": result["forecast"]["horizon"],
        })
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
