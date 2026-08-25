#!/usr/bin/env python3
"""Swarm Cognitive Drift — emergent behavioral profiles from accumulated observations."""
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


SCHEMA = "aleph.experiments.swarm-cognitive-drift.v1"
ROLLING_WINDOW = 50
SPECIES = ("sentinel", "archivist", "wanderer")
VERDICT_WEIGHTS = {"preserve": 1.0, "inspect": 0.5, "drift": -0.3}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _hash(payload: dict[str, Any]) -> str:
    material = {k: v for k, v in payload.items() if k != "drift_hash"}
    return hashlib.sha256(_canonical(material)).hexdigest()


def _clamp(value: float) -> float:
    return round(max(-1.0, min(1.0, value)), 4)


def _load_profiles() -> dict[str, Any]:
    return read_json(state_path("swarm", "cognitive_profiles.json"), {"agents": {}})


def _save_profiles(profiles: dict[str, Any]) -> None:
    write_json(state_path("swarm", "cognitive_profiles.json"), profiles)


def _update_agent_profile(
    profiles: dict[str, Any],
    agent_id: str,
    species: str,
    verdict: str,
    attention: float,
) -> dict[str, Any]:
    """Update an agent's rolling history and compute cognitive drift."""
    agent = profiles.setdefault("agents", {}).setdefault(agent_id, {
        "species": species,
        "history": [],
        "total_observations": 0,
        "drift": 0.0,
        "curiosity": 0.0,
        "caution": 0.0,
    })
    agent["total_observations"] = agent.get("total_observations", 0) + 1
    history = agent.setdefault("history", [])
    history.append({
        "verdict": verdict,
        "attention": attention,
    })
    agent["history"] = history[-ROLLING_WINDOW:]

    verdict_scores = [VERDICT_WEIGHTS.get(h["verdict"], 0) for h in agent["history"]]
    attention_scores = [h["attention"] for h in agent["history"]]
    n = max(1, len(agent["history"]))

    drift_score = sum(verdict_scores) / n
    agent["drift"] = _clamp(drift_score)

    curiosity = sum(1 for h in agent["history"] if h["verdict"] == "inspect") / n
    agent["curiosity"] = round(curiosity, 4)

    caution = sum(1 for h in agent["history"] if h["verdict"] == "preserve") / n
    agent["caution"] = round(caution, 4)

    if agent["drift"] > 0.4:
        agent["temperament"] = "preservative"
    elif agent["drift"] < -0.1:
        agent["temperament"] = "exploratory"
    else:
        agent["temperament"] = "balanced"

    agent["avg_attention"] = round(sum(attention_scores) / n, 4)
    agent["species"] = species
    return agent


def accumulate_observations(
    observations: list[dict[str, Any]],
    *,
    clock: Any = utc_now,
    record: bool = True,
) -> dict[str, Any]:
    """Ingest swarm observations and update cognitive profiles."""
    profiles = _load_profiles()
    updated_agents = []
    for obs in observations:
        agent_id = obs.get("agent_id", "")
        species = obs.get("species", "unknown")
        verdict = obs.get("verdict", "drift")
        attention = float(obs.get("attention", 0.5))
        profile = _update_agent_profile(profiles, agent_id, species, verdict, attention)
        updated_agents.append({
            "agent_id": agent_id,
            "species": species,
            "temperament": profile.get("temperament", "balanced"),
            "drift": profile.get("drift", 0.0),
            "curiosity": profile.get("curiosity", 0.0),
            "caution": profile.get("caution", 0.0),
        })

    temperaments = {}
    for entry in updated_agents:
        t = entry.get("temperament", "balanced")
        temperaments[t] = temperaments.get(t, 0) + 1

    result: dict[str, Any] = {
        "schema": SCHEMA,
        "experiment": "swarm-cognitive-drift",
        "status": "sealed",
        "mode": "data-only-behavioral-profiles",
        "sealed_at": clock(),
        "observation_count": len(observations),
        "agent_count": len(updated_agents),
        "updated_agents": updated_agents,
        "temperament_distribution": temperaments,
        "unique_temperaments": len(temperaments),
        "total_profiled_agents": len(profiles.get("agents", {})),
        "execution_enabled": False,
    }
    result["drift_hash"] = _hash(result)

    if record:
        _save_profiles(profiles)
        append_jsonl(
            ledger_path(),
            {"type": "cognitive_drift", "ref": result["drift_hash"], "agents": len(updated_agents)},
        )
    return result


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--observations", type=Path, required=True)
    p.add_argument("--no-ledger", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        obs = json.loads(args.observations.read_text())
        result = accumulate_observations(obs, record=not args.no_ledger)
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
