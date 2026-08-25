#!/usr/bin/env python3
"""Swarm Sandbox Pulse — deterministic observations over sandbox ticks."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lab.experiments.astral_socket import send
from lab.runtime_vault import append_jsonl, ledger_path, read_json, state_path, write_json
from sandbox.sandbox_engine import load_state, run_ticks


SCHEMA = "aleph.experiments.swarm-sandbox-pulse.v1"
SPECIES = ("sentinel", "archivist", "wanderer")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _hash(payload: dict[str, Any]) -> str:
    material = {key: value for key, value in payload.items() if key != "pulse_hash"}
    return hashlib.sha256(_canonical(material)).hexdigest()


def _clamp(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 4)


def _observation(cycle_id: str, tick: dict[str, Any], agent_index: int) -> dict[str, Any]:
    species = SPECIES[(agent_index + int(tick["tick"])) % len(SPECIES)]
    energy = float(tick.get("energy", 0.0))
    novelty = abs(float(tick.get("a", 0.0)) - float(tick.get("b", 0.0)))
    attention = _clamp(0.30 + energy * 0.45 + novelty * 0.35)
    if novelty >= 0.65:
        verdict, reason = "preserve", "signal divergence is high enough to archive"
    elif energy >= 0.75:
        verdict, reason = "inspect", "energy concentration crossed the inspection threshold"
    else:
        verdict, reason = "drift", "signal remains below active thresholds"
    return {
        "tick": int(tick["tick"]),
        "agent_id": f"{species}-{agent_index + 1:02d}",
        "species": species,
        "attention": attention,
        "verdict": verdict,
        "reason": reason,
        "permitted_effect": "record_observation",
        "mutation_enabled": False,
        "cycle_id": cycle_id,
    }


def swarm_sandbox_ticks(
    *,
    sandbox_ticks: int = 1,
    agent_count: int = 3,
    bus: bool = True,
    proof: bool = True,
    clock: Callable[[], str] = utc_now,
) -> dict[str, Any]:
    """Advance the sandbox and derive data-only swarm observations."""
    if not 1 <= sandbox_ticks <= 32:
        raise ValueError("sandbox-ticks must be between 1 and 32")
    if not 1 <= agent_count <= 12:
        raise ValueError("agent count must be between 1 and 12")

    before = load_state()
    sandbox = run_ticks(sandbox_ticks, proof=False)
    recent = list(sandbox.get("history", [])[-sandbox_ticks:])
    generated_at = clock()
    seed = {
        "schema": SCHEMA,
        "sandbox_before": int(before.get("ticks", 0)),
        "sandbox_after": int(sandbox.get("ticks", 0)),
        "generated_at": generated_at,
    }
    cycle_id = f"swarm-{_hash(seed)[:24]}"
    observations = [
        _observation(cycle_id, tick, agent_index)
        for tick in recent
        for agent_index in range(agent_count)
    ]
    verdict_counts = {
        verdict: sum(item["verdict"] == verdict for item in observations)
        for verdict in ("preserve", "inspect", "drift")
    }
    dominant = max(verdict_counts, key=verdict_counts.get)
    coherence = _clamp(
        verdict_counts[dominant] / max(1, agent_count * sandbox_ticks)
    )

    result: dict[str, Any] = {
        "schema": SCHEMA,
        "experiment": "swarm-sandbox-pulse",
        "status": "sealed",
        "mode": "data-only-swarm-observations",
        "cycle_id": cycle_id,
        "generated_at": generated_at,
        "sandbox_ticks_requested": sandbox_ticks,
        "sandbox_ticks_observed": len(recent),
        "sandbox_ticks_before": int(before.get("ticks", 0)),
        "sandbox_ticks_after": int(sandbox.get("ticks", 0)),
        "entropy_budget": sandbox.get("entropy_budget"),
        "novelty": sandbox.get("novelty"),
        "agent_count": agent_count,
        "observations": observations,
        "consensus": {
            **verdict_counts,
            "dominant": dominant,
            "coherence": coherence,
        },
        "authority": {
            "execution_enabled": False,
            "live_mutation_budget": 0,
            "permitted_effect": "record_observation",
        },
        "guardrails": [
            "Swarm agents observe deterministic signals only.",
            "No observation can start a process or mutate the sandbox.",
        ],
    }
    result["pulse_hash"] = _hash(result)

    state_path_value = state_path("swarm", "pulse.json")
    state_path_value.parent.mkdir(parents=True, exist_ok=True)
    history = read_json(state_path_value, {}).get("cycles", [])
    history.append({key: value for key, value in result.items() if key != "pulse_hash"})
    write_json(state_path_value, {"latest_cycle_id": cycle_id, "cycles": history[-50:]})

    bus_record = None
    if bus:
        bus_record = send(
            "swarm_sandbox_pulse",
            {
                "cycle_id": cycle_id,
                "ticks": [item["tick"] for item in recent],
                "dominant": dominant,
                "coherence": coherence,
                "execution_enabled": False,
            },
            path=state_path("swarm", "astral_channel.jsonl"),
        )
    if proof:
        append_jsonl(
            ledger_path(),
            {
                "ts": generated_at,
                "type": "swarm_sandbox_cycle",
                "ref": cycle_id,
                "observations": len(observations),
                "dominant": dominant,
                "coherence": coherence,
                "execution_enabled": False,
            },
        )
    if bus_record:
        result["bus_topic"] = bus_record["topic"]
    return result


def status() -> dict[str, Any]:
    state = read_json(state_path("swarm", "pulse.json"), {})
    latest = state.get("latest_cycle_id")
    cycles = state.get("cycles", [])
    selected = next((item for item in reversed(cycles) if item.get("cycle_id") == latest), {})
    payload = {
        "status": "ready" if selected else "dormant",
        "latest_cycle_id": latest,
        "cycles": len(cycles),
        "observations": selected.get("agent_count"),
        "dominant": selected.get("consensus", {}).get("dominant"),
    }
    print(json.dumps(payload, sort_keys=True, indent=2))
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sandbox-ticks", type=int, default=1)
    parser.add_argument("--agents", type=int, default=3)
    parser.add_argument("--no-bus", action="store_true")
    parser.add_argument("--no-proof", action="store_true")
    parser.add_argument("--status", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.status and args.sandbox_ticks == 1 and args.agents == 3:
        status()
        return 0
    try:
        result = swarm_sandbox_ticks(
            sandbox_ticks=args.sandbox_ticks,
            agent_count=args.agents,
            bus=not args.no_bus,
            proof=not args.no_proof,
        )
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
