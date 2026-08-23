#!/usr/bin/env python3
"""Bind Omega Fractal Engine affect/entropy to an IXpansion witness mesh."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ixpansion" / "src"))
sys.path.insert(0, str(ROOT))

from core.runtime import IxpansionRuntime  # noqa: E402
from omega_fractal_engine.nucleus.identity.mood_vectors import MoodEngine  # noqa: E402
from omega_fractal_engine.nucleus.kernel.entropy_regulator import EntropyRegulator  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def bridge(seed: int = 616, ticks: int = 3, *, clock=utc_now) -> dict[str, object]:
    if ticks < 1 or ticks > 64:
        raise ValueError("ticks must be between 1 and 64")
    runtime = IxpansionRuntime("hex_storm", "ring", seed)
    entropy = EntropyRegulator(target_entropy=0.58, rng_seed=seed)
    mood = MoodEngine(volatility=0.18)
    timeline = runtime.run(ticks)

    for sample in timeline:
        sample["entropy"] = entropy.regulate()
        sample["mood"] = mood.process({
            "tick": sample["tick"],
            "anomaly_count": len(sample.get("anomalies", [])),
            "witnesses": len(sample.get("witnesses", [])),
        })

    final = timeline[-1]
    signature_material = {
        "engine": "omega-fractal-ixpansion",
        "seed": seed,
        "fingerprints": [sample["fingerprint"] for sample in timeline],
        "moods": [sample["mood"] for sample in timeline],
    }
    signature = hashlib.sha256(json.dumps(signature_material, sort_keys=True).encode()).hexdigest()
    report = {
        "bridge": "omega-fractal-engine/ixpansion",
        "tick": int(final["tick"]),
        "chaos": float(final["entropy"]["current"]),
        "regime": final["entropy"]["regime"],
        "mood": str(final["mood"]),
        "mesh_delivered": sum(sample["mesh_delivered"] for sample in timeline),
        "witnesses": sum(len(sample["witnesses"]) for sample in timeline),
        "signature": signature,
        "short_signature": signature[:16],
        "created_at": clock(),
    }
    artifact = ROOT / "omega_fractal_engine" / "artifacts" / "bridge_ixpansion.json"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    temporary = artifact.with_suffix(".tmp")
    temporary.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, artifact)

    telemetry = ROOT / "nexus_observatory" / "telemetry" / "resonance.jsonl.latest"
    telemetry.parent.mkdir(parents=True, exist_ok=True)
    temporary_latest = telemetry.with_suffix(".tmp")
    temporary_latest.write_text(json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    os.replace(temporary_latest, telemetry)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Bridge Omega Fractal Engine into IXpansion")
    parser.add_argument("--seed", type=int, default=616)
    parser.add_argument("--ticks", type=int, default=3)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(bridge(args.seed, args.ticks), sort_keys=True, indent=2))
        return 0
    except (OSError, TypeError, ValueError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
