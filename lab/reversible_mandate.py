#!/usr/bin/env python3
"""Reversible Mandate Engine — bounded execution with ghost rehearsal."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
import copy
import hashlib
import json
import math
from typing import Any

from lab.pulse_oracle import _signal
from lab.ritual_parliament import oracle_is_sealed
from lab.runtime_vault import (
    append_jsonl,
    ledger_path,
    read_json,
    report_path,
    state_path,
    verify_jsonl,
    write_json,
)


SCHEMA = "aleph.chronoforge.reversible-mandate.v1"
HARD_TICK_CAP = 7
ENTROPY_FLOOR = 0.05
ROLLBACK_THRESHOLD = 0.20


def _canonical(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _hash(payload: Any) -> str:
    return hashlib.sha256(_canonical(payload)).hexdigest()


def parliament_is_sealed(parliament: dict[str, Any]) -> bool:
    if parliament.get("schema") != "aleph.chronoforge.ritual-parliament.v1":
        return False
    if parliament.get("status") != "sealed" or not parliament.get("parliament_hash"):
        return False
    body = {key: value for key, value in parliament.items() if key != "parliament_hash"}
    return _hash(body) == parliament["parliament_hash"]


def _refusal(reason: str) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "experiment": "reversible-mandate",
        "status": "refused",
        "reason": reason,
    }


def _advance(state: dict[str, Any], projection: dict[str, Any], multiplier: float) -> None:
    tick = int(state["ticks"])
    phase = float(state["phase"])
    alpha, beta = _signal(tick, phase)
    raw_energy = float(projection["energy"]) * multiplier
    energy = min(1.0, max(0.0, raw_energy))
    budget = max(ENTROPY_FLOOR, float(state["entropy_budget"]) - 0.01 * energy)
    next_phase = (phase + 0.17 + 0.05 * alpha) % (2 * math.pi)
    state["ticks"] = tick + 1
    state["entropy_budget"] = round(budget, 4)
    state["phase"] = round(next_phase, 4)
    state["novelty"] = round(abs(alpha - beta), 4)
    history = [item for item in state.get("history", []) if isinstance(item, dict)]
    history.append({"tick": tick + 1, "a": round(alpha, 5), "b": round(beta, 5), "energy": round(energy, 5)})
    state["history"] = history[-50:]


def rehearse(
    sandbox_state: dict[str, Any],
    parliament: dict[str, Any],
    max_ticks: int | None = None,
) -> tuple[dict[str, Any], int]:
    """Return a ghost timeline after applying the mandate without touching disk."""
    oracle = parliament.get("oracle")
    directive = parliament.get("directive")
    projections = oracle["forecast"]["projections"]
    requested = min(
        int(directive["allowed_ticks_per_window"]),
        len(projections),
        HARD_TICK_CAP,
    )
    if max_ticks is not None:
        requested = min(requested, max_ticks)
    ghost = copy.deepcopy(sandbox_state)
    multiplier = float(directive["consumption_multiplier"])
    for projection in projections[:requested]:
        _advance(ghost, projection, multiplier)
    return ghost, requested


def _preflight(
    parliament: dict[str, Any],
    sandbox_state: dict[str, Any],
    audit: dict[str, Any],
    max_ticks: int | None,
) -> tuple[dict[str, Any], int] | dict[str, Any]:
    if not parliament_is_sealed(parliament):
        return _refusal("missing, unsealed, or modified parliament")
    oracle = parliament.get("oracle")
    if not isinstance(oracle, dict) or not oracle_is_sealed(oracle):
        return _refusal("embedded oracle is missing, unsealed, or modified")
    if parliament.get("oracle_hash") != oracle.get("oracle_hash"):
        return _refusal("parliament and embedded oracle disagree")
    if not parliament.get("quorum_met"):
        return _refusal("parliament lacked a two-faction quorum")
    if not audit.get("ok"):
        return _refusal("proof ledger audit failed")
    if sandbox_state.get("status") == "running":
        return _refusal("sandbox is already running")
    forecast_tick = int(oracle.get("signals", {}).get("sandbox_ticks", -1))
    if int(sandbox_state.get("ticks", -2)) != forecast_tick:
        return _refusal("mandate is stale relative to sandbox ticks")
    directive = parliament.get("directive")
    policy = parliament.get("chosen_policy")
    if not isinstance(directive, dict) or policy not in {"ration", "stabilize", "expand"}:
        return _refusal("unsupported directive")
    multiplier = float(directive.get("consumption_multiplier", 0))
    if multiplier <= 0 or multiplier > 1.5:
        return _refusal("consumption multiplier outside safety bounds")
    if max_ticks is not None and not 1 <= max_ticks <= HARD_TICK_CAP:
        return _refusal(f"max-ticks must be between 1 and {HARD_TICK_CAP}")
    budget = float(sandbox_state.get("entropy_budget", 0))
    if budget < ENTROPY_FLOOR:
        return _refusal("entropy hard floor already breached")
    ghost, ticks = rehearse(sandbox_state, parliament, max_ticks)
    if ticks < 1:
        return _refusal("directive has no executable tick budget")
    final_budget = float(ghost["entropy_budget"])
    if final_budget < ENTROPY_FLOOR:
        return _refusal("rehearsal breaches the entropy hard floor")
    if policy != "ration" and final_budget < ROLLBACK_THRESHOLD:
        return _refusal("non-ration rehearsal crosses the rollback threshold")
    return ghost, ticks


def execute(
    parliament_report: dict[str, Any],
    *,
    max_ticks: int | None = None,
    dry_run: bool = False,
    ledger_records: bool = True,
) -> dict[str, Any]:
    """Rehearse a sealed mandate, then execute it with per-tick witnesses."""
    audit = verify_jsonl(ledger_path())
    preflight = _preflight(parliament_report, read_json(state_path("sandbox", "engine.json"), {}), audit, max_ticks)
    if len(preflight) == 2 and "reason" not in preflight:
        ghost, planned_ticks = preflight
    else:
        result = preflight
        write_json(report_path("reversible-mandate.json"), result)
        print(json.dumps(result, sort_keys=True, indent=2))
        return result

    sandbox_state = read_json(state_path("sandbox", "engine.json"), {})
    base_body = {key: value for key, value in sandbox_state.items() if key != "status"}
    result = {
        "schema": SCHEMA,
        "experiment": "reversible-mandate",
        "status": "rehearsed" if dry_run else "sealed",
        "chosen_policy": parliament_report["chosen_policy"],
        "parliament_hash": parliament_report["parliament_hash"],
        "oracle_hash": parliament_report["oracle_hash"],
        "oracle": parliament_report["oracle"],
        "planned_ticks": planned_ticks,
        "ghost_final_budget": ghost["entropy_budget"],
        "ghost_peak_energy": max(
            float(item["energy"])
            for item in ghost.get("history", [])
            if int(item.get("tick", 0)) > int(sandbox_state.get("ticks", 0))
        ),
        "witnesses": [],
        "rollback_trigger": parliament_report["directive"]["rollback_trigger"],
        "hard_floor": ENTROPY_FLOOR,
    }
    if dry_run:
        result["execution_certificate"] = _hash(result)
        write_json(report_path("reversible-mandate.json"), result)
        print(json.dumps(result, sort_keys=True, indent=2))
        return result

    snapshot = copy.deepcopy(sandbox_state)
    executed: list[dict[str, Any]] = []
    projections = parliament_report["oracle"]["forecast"]["projections"]
    multiplier = float(parliament_report["directive"]["consumption_multiplier"])
    policy = parliament_report["chosen_policy"]
    try:
        for projection in projections[:planned_ticks]:
            before_hash = _hash({key: value for key, value in sandbox_state.items() if key != "status"})
            _advance(sandbox_state, projection, multiplier)
            after_hash = _hash({key: value for key, value in sandbox_state.items() if key != "status"})
            witness = {
                "type": "mandate_tick",
                "policy": policy,
                "tick": sandbox_state["ticks"],
                "energy": sandbox_state["history"][-1]["energy"],
                "entropy_budget": sandbox_state["entropy_budget"],
                "before_hash": before_hash,
                "after_hash": after_hash,
                "parliament_hash": parliament_report["parliament_hash"],
                "oracle_hash": parliament_report["oracle_hash"],
            }
            sealed_witness = append_jsonl(ledger_path(), witness)
            write_json(state_path("sandbox", "engine.json"), sandbox_state)
            executed.append(witness)
            result["witnesses"].append({
                "entry_hash": sealed_witness["entry_hash"], "tick": witness["tick"],
                "before_hash": before_hash, "after_hash": after_hash,
            })
            if policy != "ration" and float(sandbox_state["entropy_budget"]) < ROLLBACK_THRESHOLD:
                raise RuntimeError("live rollback trigger crossed")
        if ledger_records:
            append_jsonl(ledger_path(), {
                "type": "mandate_complete",
                "policy": policy,
                "ticks": planned_ticks,
                "final_entropy_budget": sandbox_state["entropy_budget"],
                "parliament_hash": parliament_report["parliament_hash"],
            })
        result["final_entropy_budget"] = sandbox_state["entropy_budget"]
    except Exception as error:
        write_json(state_path("sandbox", "engine.json"), snapshot)
        append_jsonl(ledger_path(), {
            "type": "mandate_rollback",
            "policy": policy,
            "executed_witnesses": len(executed),
            "reason": str(error),
            "restored_after_hash": _hash({key: value for key, value in snapshot.items() if key != "status"}),
            "parliament_hash": parliament_report["parliament_hash"],
        })
        result.update({
            "status": "rolled_back",
            "reason": str(error),
            "executed_witnesses": len(executed),
            "restored_entropy_budget": snapshot["entropy_budget"],
        })

    chained = verify_jsonl(ledger_path())
    result["ledger_audit_ok"] = bool(chained.get("ok"))
    if not chained.get("ok"):
        result["status"] = "unverified"
    result["execution_certificate"] = _hash(result)
    write_json(report_path("reversible-mandate.json"), result)
    print(json.dumps(result, sort_keys=True, indent=2))
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=None, help="sealed Ritual Parliament report")
    parser.add_argument("--max-ticks", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true", help="rehearse without mutating state")
    parser.add_argument("--no-ledger", action="store_true", help="omit completion record; tick witnesses remain mandatory")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    source = args.report or report_path("ritual-parliament.json")
    parliament = read_json(source, {})
    result = execute(
        parliament,
        max_ticks=args.max_ticks,
        dry_run=args.dry_run,
        ledger_records=not args.no_ledger,
    )
    return 0 if result["status"] in {"sealed", "rehearsed"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
