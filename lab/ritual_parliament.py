#!/usr/bin/env python3
"""Ritual Parliament — deterministic policy debate over a sealed Pulse Oracle."""
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

from lab.runtime_vault import (
    append_jsonl,
    ledger_path,
    read_json,
    report_path,
    write_json,
)


SCHEMA = "aleph.chronoforge.ritual-parliament.v1"
ZERO_HASH = "0" * 64
FACTIONS = {
    "conservator": {"risk": 0.25, "authority": {"ration": 0.25, "stabilize": 0.06, "expand": 0.00}},
    "stabilizer": {"risk": 0.55, "authority": {"ration": 0.05, "stabilize": 0.10, "expand": 0.00}},
    "explorer": {"risk": 0.90, "authority": {"ration": 0.00, "stabilize": 0.03, "expand": 0.25}},
}
POLICIES = {
    "ration": {"risk": 0.20, "consumption": 0.45, "novelty": 0.55, "ticks": 1},
    "stabilize": {"risk": 0.55, "consumption": 0.75, "novelty": 0.95, "ticks": 2},
    "expand": {"risk": 0.90, "consumption": 1.10, "novelty": 1.35, "ticks": 3},
}
FACTION_WEIGHTS = {
    "conservator": {"safety": 0.45, "viability": 0.35, "opportunity": 0.05, "evidence": 0.15},
    "stabilizer": {"safety": 0.20, "viability": 0.35, "opportunity": 0.30, "evidence": 0.15},
    "explorer": {"safety": 0.12, "viability": 0.25, "opportunity": 0.48, "evidence": 0.15},
}


def _canonical(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def oracle_is_sealed(oracle: dict[str, Any]) -> bool:
    if oracle.get("status") != "sealed" or not oracle.get("oracle_hash"):
        return False
    body = {key: value for key, value in oracle.items() if key != "oracle_hash"}
    return hashlib.sha256(_canonical(body)).hexdigest() == oracle["oracle_hash"]


def _clamp(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 5)


def _simulate(policy_name: str, oracle: dict[str, Any]) -> dict[str, Any]:
    policy = POLICIES[policy_name]
    projections = oracle["forecast"]["projections"]
    budget = float(oracle["signals"]["entropy_budget"])
    projected_budgets = []
    novelty_total = 0.0
    energy_values = []
    for projection in projections:
        energy = min(1.0, max(0.0, float(projection["energy"]) * policy["consumption"]))
        budget = max(0.05, budget - 0.01 * energy)
        favorable_window = max(0.0, 1.0 - abs(energy - 0.58) / 0.45)
        novelty_total += favorable_window * policy["novelty"]
        projected_budgets.append(round(budget, 5))
        energy_values.append(energy)
    average_energy = sum(energy_values) / max(len(energy_values), 1)
    return {
        "policy": policy_name,
        "ticks": min(int(policy["ticks"]), len(projections)),
        "projected_budget": projected_budgets[-1],
        "average_energy": _clamp(average_energy),
        "opportunity_pressure": _clamp(novelty_total / max(len(projections), 1)),
        "safety": _clamp(sum(max(0.0, 1.0 - value) for value in energy_values) / max(len(energy_values), 1)),
        "viability": _clamp(projected_budgets[-1]),
        "risk_gate": _clamp(
            1.0 if projected_budgets[-1] >= 0.45 else
            0.75 + (projected_budgets[-1] - 0.20) * (0.25 / 0.25) if projected_budgets[-1] >= 0.20 else
            0.35 + max(0.0, projected_budgets[-1] - 0.05) * (0.40 / 0.15)
        ),
    }


def deliberate(oracle: dict[str, Any]) -> dict[str, Any]:
    """Run the three-faction parliament against one sealed Oracle forecast."""
    if not oracle_is_sealed(oracle):
        raise ValueError("refusing an unsealed or modified pulse oracle")
    simulations = {name: _simulate(name, oracle) for name in POLICIES}
    verdict = oracle["verdict"]
    ballots = []
    scores: dict[str, dict[str, float]] = {name: {} for name in FACTIONS}
    for faction, traits in FACTIONS.items():
        ballot = {}
        for candidate, simulation in simulations.items():
            alignment = 1 - abs(float(traits["risk"]) - float(POLICIES[candidate]["risk"]))
            weights = FACTION_WEIGHTS[faction]
            raw_score = (
                weights["safety"] * simulation["safety"]
                + weights["viability"] * simulation["viability"]
                + weights["opportunity"] * simulation["opportunity_pressure"]
                + weights["evidence"] * float(oracle.get("confidence", 0))
                + float(traits["authority"].get(candidate, 0))
                + (0.08 if candidate == verdict else 0)
            )
            if simulation["projected_budget"] < 0.20 and candidate != "ration":
                raw_score = min(raw_score, 0.28)
            score = simulation["risk_gate"] * raw_score
            ballot[candidate] = _clamp(score)
            scores[faction][candidate] = ballot[candidate]
        ranked = sorted(ballot, key=lambda name: (-ballot[name], name))
        ballots.append({"faction": faction, "ranking": ranked, "scores": ballot})

    borda = {candidate: 0.0 for candidate in POLICIES}
    for ballot in ballots:
        for index, candidate in enumerate(ballot["ranking"]):
            borda[candidate] += len(POLICIES) - index - 1
    ranking = sorted(borda, key=lambda name: (-borda[name], name != verdict, name))
    chosen = ranking[0]
    runner_up = ranking[1]
    margin = _clamp((borda[chosen] - borda[runner_up]) / max(2 * (len(POLICIES) - 1), 1))
    coalition = [ballot["faction"] for ballot in ballots if ballot["ranking"][0] == chosen]

    result = {
        "schema": SCHEMA,
        "experiment": "ritual-parliament",
        "status": "sealed",
        "oracle_hash": oracle["oracle_hash"],
        "verdict": verdict,
        "chosen_policy": chosen,
        "coalition": coalition,
        "borda": {name: round(value, 5) for name, value in sorted(borda.items())},
        "margin": margin,
        "quorum": "two-of-three first-choice votes",
        "quorum_met": len(coalition) >= 2,
        "simulations": simulations,
        "ballots": ballots,
        "directive": {
            "allowed_ticks_per_window": POLICIES[chosen]["ticks"],
            "consumption_multiplier": POLICIES[chosen]["consumption"],
            "mandatory_witness_each_tick": True,
            "rollback_trigger": "entropy_budget < 0.20",
            "stop_condition": "any failed ledger audit",
            "fallback_policy": runner_up,
        },
    }
    result["parliament_hash"] = hashlib.sha256(_canonical(result)).hexdigest()
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--no-ledger", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    source = args.report or report_path("pulse-oracle.json")
    oracle = read_json(source, {})
    try:
        result = deliberate(oracle)
    except (ValueError, KeyError, TypeError):
        failure = {
            "schema": SCHEMA, "status": "refused", "source": str(source),
            "reason": "missing, unsealed, or modified pulse oracle",
        }
        write_json(report_path("ritual-parliament.json"), failure)
        print(json.dumps(failure, sort_keys=True, indent=2))
        return 1
    write_json(report_path("ritual-parliament.json"), result)
    if not args.no_ledger:
        append_jsonl(ledger_path(), {
            "type": "ritual_parliament",
            "chosen_policy": result["chosen_policy"],
            "parliament_hash": result["parliament_hash"],
            "oracle_hash": result["oracle_hash"],
        })
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
