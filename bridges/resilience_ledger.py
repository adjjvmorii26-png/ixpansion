"""Resilience Ledger — measure whether counterfactual wounds heal.

A divergence is not finished at its birth.  This module applies identical
recovery experiences to both realities and records whether exact semantics
repair themselves, whether only telemetry heals, whether history remains
plastic, or whether an apparent recovery later relapses.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from bridges.counterfactual_twin import CounterfactualTwin, Signal
from bridges.divergence_forensics import diagnosis_from_twin_outcome
from bridges.resonance_loom import _atomic_write

STATUS_FIELDS = ("chaos", "mood", "mesh_events", "reactor_events", "state_keys")


@dataclass(frozen=True)
class RecoverySample:
    """One post-perturbation observation of both worlds."""

    tick: int
    label: str
    semantic_changed: bool
    resonance_changed: bool
    semantic_magnitude: float
    resonance_magnitude: float
    camouflage_index: float
    signature_distance: int
    changed_paths: tuple[str, ...]

    def payload(self) -> dict[str, Any]:
        value = asdict(self)
        value["changed_paths"] = list(self.changed_paths)
        return value


def _sample_from_outcome(outcome: dict[str, Any]) -> RecoverySample:
    diagnosis = diagnosis_from_twin_outcome(outcome).payload()
    return RecoverySample(
        tick=int(outcome["tick"]),
        label=str(outcome["label"]),
        semantic_changed=bool(diagnosis["semantic_changed"]),
        resonance_changed=bool(diagnosis["resonance_changed"]),
        semantic_magnitude=float(diagnosis["semantic_magnitude"]),
        resonance_magnitude=float(diagnosis["resonance_magnitude"]),
        camouflage_index=float(diagnosis["camouflage_index"]),
        signature_distance=int(diagnosis["signature_distance"]),
        changed_paths=tuple(diagnosis["changed_paths"]),
    )


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, round(value, 6)))


class ResilienceLedger:
    """Probe how paired worlds respond to identical recovery pressure."""

    def __init__(self, seed: int | None = None) -> None:
        self.seed = seed

    def probe(
        self,
        interventions: list[tuple[Signal, Signal]],
        recoveries: list[Signal],
        *,
        labels: list[str] | None = None,
    ) -> dict[str, Any]:
        """Apply paired wounds followed by identical recovery experiences."""
        if not interventions:
            raise ValueError("at least one intervention is required")

        twin = CounterfactualTwin(seed=self.seed)
        twin.run(interventions, labels=labels)
        wound_outcomes = list(twin.timeline)
        if not wound_outcomes:
            raise ValueError("counterfactual timeline is empty")
        wound_samples = [_sample_from_outcome(item) for item in wound_outcomes]
        initial_sample = wound_samples[-1]

        recovery_samples: list[RecoverySample] = []
        for index, signal in enumerate(recoveries, start=1):
            _, _ = twin.step(signal, signal, label=f"recovery-{index}")
            recovery_samples.append(_sample_from_outcome(twin.timeline[-1]))

        observations = wound_samples + recovery_samples
        semantic_recovered_at = next(
            (item.tick for item in recovery_samples if not item.semantic_changed),
            None,
        )
        # Index in recovery sequence, not absolute twin tick.
        recovery_sequence_tick = next(
            (
                index for index, item in enumerate(recovery_samples, start=1)
                if not item.semantic_changed
            ),
            None,
        )
        ever_recovered = recovery_sequence_tick is not None
        final_sample = recovery_samples[-1] if recovery_samples else initial_sample
        final_semantic_recovered = not final_sample.semantic_changed
        final_resonance_recovered = not final_sample.resonance_changed

        if not initial_sample.semantic_changed:
            classification = "inert_perturbation"
        elif final_semantic_recovered and recovery_sequence_tick == 1:
            classification = "elastic_recovery"
        elif final_semantic_recovered:
            classification = "delayed_recovery"
        elif ever_recovered:
            classification = "relapsed_divergence"
        elif final_resonance_recovered:
            classification = "hysteretic_trace"
        else:
            classification = "plastic_divergence"

        initial_magnitude = initial_sample.semantic_magnitude
        final_magnitude = final_sample.semantic_magnitude
        recovery_efficiency = (
            _clamp01(1.0 - final_magnitude / initial_magnitude)
            if initial_magnitude > 0
            else 1.0
        )
        evidence_inputs = {
            "classification": classification,
            "interventions": [
                {"baseline": baseline.payload(), "twin": twin.payload()}
                for baseline, twin in interventions
            ],
            "recoveries": [signal.payload() for signal in recoveries],
            "samples": [item.payload() for item in observations],
            "seed": self.seed,
        }
        canonical = json.dumps(evidence_inputs, sort_keys=True, separators=(",", ":"))
        evidence_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

        return {
            "experiment": "resilience-ledger",
            "engine_version": 1,
            "seed": self.seed,
            "classification": classification,
            "wound_count": len(interventions),
            "recovery_experience_count": len(recoveries),
            "initial_wound": initial_sample.payload(),
            "final_state": final_sample.payload(),
            "semantic_recovered_at_tick": semantic_recovered_at,
            "semantic_recovered_after_experiences": recovery_sequence_tick,
            "final_semantic_recovered": final_semantic_recovered,
            "final_resonance_recovered": final_resonance_recovered,
            "recovery_efficiency": recovery_efficiency,
            "evidence_hash": evidence_hash,
            "wound_timeline": [item.payload() for item in wound_samples],
            "recovery_timeline": [item.payload() for item in recovery_samples],
        }

    def probe_single(
        self,
        baseline: Signal,
        twin: Signal,
        recovery: Signal,
        *,
        recovery_steps: int = 3,
        label: str = "counterfactual-wound",
    ) -> dict[str, Any]:
        """Convenience API for one wound and one repeated recovery experience."""
        if recovery_steps < 0:
            raise ValueError("recovery_steps cannot be negative")
        return self.probe(
            [(baseline, twin)],
            [recovery] * recovery_steps,
            labels=[label],
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Measure counterfactual resilience")
    parser.add_argument("--seed", type=int, default=None)
    commands = parser.add_subparsers(dest="command", required=True)
    probe = commands.add_parser("probe", help="probe one wound and repeated recovery")
    probe.add_argument("--output", type=Path, required=True)
    probe.add_argument("--agent", required=True)
    probe.add_argument("--baseline-valence", type=float, default=0.25)
    probe.add_argument("--baseline-arousal", type=float, default=0.65)
    probe.add_argument("--twin-valence", type=float, default=-0.35)
    probe.add_argument("--twin-arousal", type=float, default=0.75)
    probe.add_argument("--recovery-agent", default=None)
    probe.add_argument("--recovery-valence", type=float, default=0.0)
    probe.add_argument("--recovery-arousal", type=float, default=0.5)
    probe.add_argument("--recovery-steps", type=int, default=3)
    probe.add_argument("--label", default="counterfactual-wound")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = ResilienceLedger(seed=args.seed).probe_single(
            Signal(args.agent, args.baseline_valence, args.baseline_arousal),
            Signal(args.agent, args.twin_valence, args.twin_arousal),
            Signal(args.recovery_agent or args.agent, args.recovery_valence, args.recovery_arousal),
            recovery_steps=args.recovery_steps,
            label=args.label,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        rendered = json.dumps(report, sort_keys=True, indent=2) + "\n"
        _atomic_write(args.output, rendered)
        print(json.dumps({
            "output": str(args.output),
            "classification": report["classification"],
            "recovery_efficiency": report["recovery_efficiency"],
            "evidence_hash": report["evidence_hash"],
        }, sort_keys=True))
        return 0
    except (OSError, ValueError) as error:
        print(json.dumps({"error": str(error)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
