#!/usr/bin/env python3
"""Ancestral Echo Engine — rehearse inherited behavior against the present world."""
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

from lab.mandate_genome import find_genome, load_genomes
from lab.pulse_oracle import forecast, seal_oracle
from lab.reversible_mandate import (
    ENTROPY_FLOOR,
    HARD_TICK_CAP,
    ROLLBACK_THRESHOLD,
    rehearse,
)
from lab.ritual_parliament import POLICIES, deliberate
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


SCHEMA = "aleph.chronoforge.genome-echo.v1"
TRAITS = ("risk_appetite", "patience", "curiosity", "conservation", "resilience")
POLICY_RISK = {"ration": 0.20, "stabilize": 0.55, "expand": 0.90}


def _canonical(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _hash(payload: Any) -> str:
    return hashlib.sha256(_canonical(payload)).hexdigest()


def _clamp(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 5)


def echo_is_sealed(report: dict[str, Any]) -> bool:
    """Validate the final report even after transport metadata is attached."""
    if report.get("schema") != SCHEMA or report.get("status") != "sealed":
        return False
    claimed = report.get("echo_hash")
    if not claimed:
        return False
    body = {
        key: value
        for key, value in report.items()
        if key not in {"echo_hash", "ledger_entry_hash", "sequence", "previous_hash", "entry_hash"}
    }
    return _hash(body) == claimed


def _state_signature(state: dict[str, Any]) -> dict[str, Any]:
    history = [item for item in state.get("history", []) if isinstance(item, dict)][-7:]
    return {
        "entropy_budget": round(float(state.get("entropy_budget", 0)), 5),
        "novelty": round(float(state.get("novelty", 0)), 5),
        "phase": round(float(state.get("phase", 0)), 5),
        "ticks": int(state.get("ticks", 0)),
        "recent_history": history,
    }


def _traits_from_parliament(parliament: dict[str, Any], final_budget: float) -> dict[str, float]:
    policy = parliament["chosen_policy"]
    energy_values = [
        min(1.0, max(0.0, float(item["energy"]) * float(parliament["directive"]["consumption_multiplier"])))
        for item in parliament["oracle"]["forecast"]["projections"]
    ]
    energy = sum(energy_values) / max(len(energy_values), 1)
    ticks = min(
        int(parliament["directive"]["allowed_ticks_per_window"]),
        len(parliament["oracle"]["forecast"]["projections"]),
        HARD_TICK_CAP,
    )
    base_risk = POLICY_RISK[policy]
    return {
        "risk_appetite": _clamp(base_risk * 0.70 + (1.0 - final_budget) * 0.20 + energy * 0.10),
        "patience": _clamp(1.0 - ticks / HARD_TICK_CAP),
        "curiosity": _clamp(energy),
        "conservation": _clamp(1.0 - final_budget),
        "resilience": 1.0,
    }


def _distance(first: dict[str, float], second: dict[str, float]) -> float:
    return sum(abs(float(first[name]) - float(second[name])) for name in TRAITS) / len(TRAITS)


def echo(
    genome_id: str,
    *,
    current_state: dict[str, Any] | None = None,
    max_ticks: int | None = None,
    record: bool = True,
) -> dict[str, Any]:
    """Rehearse one verified genome against the present world without mutation."""
    if max_ticks is not None and not 1 <= max_ticks <= HARD_TICK_CAP:
        raise ValueError(f"max-ticks must be between 1 and {HARD_TICK_CAP}")
    genomes = load_genomes()
    if genome_id == "@latest":
        if not genomes:
            raise ValueError("no genomes are available for @latest")
        genome = genomes[-1]
    else:
        genome = find_genome(genome_id, genomes)
    state = read_json(state_path("sandbox", "engine.json"), {}) if current_state is None else current_state
    if not isinstance(state, dict) or "ticks" not in state or "entropy_budget" not in state:
        raise ValueError("current sandbox state is missing or malformed")
    if state.get("status") == "running":
        raise ValueError("cannot echo while the sandbox is running")

    audit = verify_jsonl(ledger_path())
    if not audit.get("ok"):
        raise ValueError("proof ledger audit failed")
    records = read_jsonl(ledger_path())
    synthetic_oracle = seal_oracle(forecast(
        sandbox_state=state,
        pulse_state=read_json(state_path("pulse", "state.json"), {}),
        flux_state=read_json(state_path("worlds", "flux.json"), {}),
        ledger_records=records,
        audit=audit,
        horizon=HARD_TICK_CAP,
    ))
    synthetic_parliament = deliberate(synthetic_oracle)

    signature = _state_signature(state)
    result = {
        "schema": SCHEMA,
        "experiment": "ancestral-echo",
        "status": "sealed",
        "genome_id": genome["genome_id"],
        "genome_hash": genome["genome_hash"],
        "original_outcome": genome.get("outcome"),
        "original_policy": genome.get("policy"),
        "original_traits": genome.get("traits", {}),
        "generation": genome.get("generation"),
        "current_state_signature": signature,
        "current_state_signature_hash": "",
        "echo_policy": synthetic_parliament.get("chosen_policy"),
        "projected_ticks": 0,
        "projected_final_budget": None,
        "echo_traits": {},
        "policy_alignment": 0.0,
        "trait_distance": 1.0,
        "vitality": 0.0,
        "resonance": 0.0,
        "verdict": "dormant",
        "refusal": None,
        "max_ticks": max_ticks,
    }
    result["current_state_signature_hash"] = _hash(signature)

    def finish() -> dict[str, Any]:
        result["echo_hash"] = _hash({
            key: value for key, value in result.items()
            if key not in {"echo_hash", "ledger_entry_hash"}
        })
        if record:
            sealed = append_jsonl(
                ledger_path("genome-echoes.jsonl"),
                {key: value for key, value in result.items() if key != "ledger_entry_hash"},
            )
            result["ledger_entry_hash"] = sealed["entry_hash"]
            write_json(report_path("genome-echo.json"), result)
        return result

    if not synthetic_parliament.get("quorum_met"):
        result["refusal"] = "present-world parliament lacked quorum"
        return finish()

    try:
        ghost, ticks = rehearse(state, synthetic_parliament, max_ticks)
    except (KeyError, TypeError, ValueError) as error:
        result["refusal"] = f"echo rehearsal refused: {error}"
        return finish()

    final_budget = float(ghost["entropy_budget"])
    result["projected_ticks"] = ticks
    result["projected_final_budget"] = final_budget
    result["echo_traits"] = _traits_from_parliament(synthetic_parliament, final_budget)
    original_traits = {
        name: float(genome.get("traits", {}).get(name, 0.0))
        for name in TRAITS
    }

    original_risk = POLICY_RISK.get(genome.get("policy"), 0.0)
    echo_risk = POLICY_RISK[result["echo_policy"]]
    alignment = _clamp(1.0 - abs(original_risk - echo_risk) / 0.70)
    distance = _clamp(_distance(original_traits, result["echo_traits"]))
    vitality = _clamp((final_budget - ENTROPY_FLOOR) / (ROLLBACK_THRESHOLD - ENTROPY_FLOOR))

    result.update({
        "policy_alignment": alignment,
        "trait_distance": distance,
        "vitality": vitality,
        "resonance": _clamp(0.45 * alignment + 0.35 * (1.0 - distance) + 0.20 * vitality),
    })
    if result["echo_policy"] == genome.get("policy") and result["resonance"] >= 0.78:
        result["verdict"] = "resonant"
    elif result["resonance"] >= 0.58:
        result["verdict"] = "drifting"
    else:
        result["verdict"] = "fossilized"

    if final_budget < ENTROPY_FLOOR:
        result["verdict"] = "quarantined"
        result["refusal"] = "echo breaches the entropy hard floor"
    elif result["echo_policy"] != "ration" and final_budget < ROLLBACK_THRESHOLD:
        result["verdict"] = "quarantined"
        result["refusal"] = "non-ration echo crosses the rollback threshold"
    return finish()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("genome_id", help="genome ID, or @latest for the most recent lineage")
    parser.add_argument("--state", type=Path, default=None, help="JSON file containing the current sandbox state")
    parser.add_argument("--max-ticks", type=int, default=None)
    parser.add_argument("--no-ledger", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        state = read_json(args.state, {}) if args.state else None
        result = echo(args.genome_id, current_state=state, max_ticks=args.max_ticks, record=not args.no_ledger)
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (KeyError, TypeError, ValueError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, sort_keys=True, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
