"""Counterfactual Twin — replay two realities until they split.

The twin starts with identically seeded engines and applies paired signals. It
records the first semantic boundary (different exact state) independently from
the first resonance boundary (different telemetry fingerprint).
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from bridges.bridge_core import BridgeHub
from bridges.divergence_forensics import diagnose_divergence, diff_state
from bridges.resonance_loom import ResonanceLoom, _atomic_write


@dataclass(frozen=True)
class Signal:
    """Affective stimulus injected into one reality."""

    agent_id: str
    valence: float
    arousal: float

    def payload(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Intervention:
    """A paired pair of signals defining a counterfactual boundary."""

    baseline: Signal
    twin: Signal


class CounterfactualTwin:
    """Advance identical universes and locate their first causal split."""

    def __init__(self, seed: int | None = None) -> None:
        self.seed = seed
        self.baseline_hub = BridgeHub(seed=seed)
        self.twin_hub = BridgeHub(seed=seed)
        self.baseline_loom = ResonanceLoom(hub=self.baseline_hub)
        self.twin_loom = ResonanceLoom(hub=self.twin_hub)

        self.timeline: list[dict[str, Any]] = []
        self.origin_baseline = self.baseline_loom.observe("counterfactual-origin")
        self.origin_twin = self.twin_loom.observe("counterfactual-origin")
        if self.origin_baseline.signature != self.origin_twin.signature:
            raise ValueError("counterfactual origins failed to synchronize")

    @staticmethod
    def _changed_fields(
        baseline_status: dict[str, Any], twin_status: dict[str, Any]
    ) -> list[str]:
        return sorted(
            field for field in baseline_status if baseline_status[field] != twin_status[field]
        )

    @staticmethod
    def _distance(old: str, new: str) -> int:
        """Return hexadecimal signature distance over equal-length digests."""
        return sum(a != b for a, b in zip(old, new)) + abs(len(old) - len(new))

    def _boundary(
        self,
        *,
        step_index: int,
        label: str,
        intervention: Intervention,
        baseline_pulse_payload: dict[str, Any],
        twin_pulse_payload: dict[str, Any],
        semantic_match: bool,
        resonance_match: bool,
    ) -> dict[str, Any]:
        baseline_status = {
            field: baseline_pulse_payload[field]
            for field in ("chaos", "mood", "mesh_events", "reactor_events", "state_keys")
        }
        twin_status = {
            field: twin_pulse_payload[field]
            for field in ("chaos", "mood", "mesh_events", "reactor_events", "state_keys")
        }
        old, new = baseline_pulse_payload["signature"], twin_pulse_payload["signature"]
        distance = self._distance(old, new)
        if not semantic_match:
            divergence_kind = "semantic"
        elif not resonance_match:
            divergence_kind = "resonance"
        else:
            divergence_kind = "none"

        return {
            "step_index": step_index,
            "tick": baseline_pulse_payload["tick"],
            "label": label,
            "kind": divergence_kind,
            "agent_id": intervention.baseline.agent_id,
            "baseline_signal": intervention.baseline.payload(),
            "twin_signal": intervention.twin.payload(),
            "distance": distance,
            "similarity": max(0.0, round(1.0 - distance / 64, 4)),
            "changed_status_fields": self._changed_fields(baseline_status, twin_status),
            "changed_paths": [
                delta["path"] for delta in diff_state(
                    self.baseline_hub.state_core.raw,
                    self.twin_hub.state_core.raw,
                )
            ],
            "state_changed": not semantic_match,
            "resonance_changed": not resonance_match,
            "baseline_signature": old,
            "twin_signature": new,
        }

    def step(
        self,
        baseline: Signal,
        twin: Signal,
        *,
        label: str = "intervention",
    ) -> tuple[dict[str, Any], dict[str, Any] | None]:
        """Apply one paired intervention and return its outcome and boundary."""
        self.baseline_loom.hub.set_state(
            baseline.agent_id, {"valence": baseline.valence, "arousal": baseline.arousal}
        )
        self.twin_loom.hub.set_state(
            twin.agent_id, {"valence": twin.valence, "arousal": twin.arousal}
        )
        self.baseline_loom.hub.propagate_emotion(baseline.agent_id)
        self.twin_loom.hub.propagate_emotion(twin.agent_id)
        self.baseline_loom.hub.route_event(
            "meta", "counterfactual_signal", baseline.payload()
        )
        self.twin_loom.hub.route_event("meta", "counterfactual_signal", twin.payload())

        baseline_pulse = self.baseline_loom.observe(f"baseline:{label}")
        twin_pulse = self.twin_loom.observe(f"twin:{label}")
        baseline_payload, twin_payload = baseline_pulse.payload(), twin_pulse.payload()
        semantic_match = (
            self.baseline_hub.state_core.snapshot() == self.twin_hub.state_core.snapshot()
        )
        resonance_match = baseline_pulse.signature == twin_pulse.signature

        outcome = {
            "tick": baseline_payload["tick"],
            "label": label,
            "semantic_match": semantic_match,
            "resonance_match": resonance_match,
            "baseline": baseline_payload,
            "twin": twin_payload,
            "baseline_state": self.baseline_hub.state_core.raw,
            "twin_state": self.twin_hub.state_core.raw,
            "baseline_state_snapshot": self.baseline_hub.state_core.snapshot(),
            "twin_state_snapshot": self.twin_hub.state_core.snapshot(),
            "state_delta": diff_state(
                self.baseline_hub.state_core.raw,
                self.twin_hub.state_core.raw,
            ),
        }
        boundary = None
        if not semantic_match or not resonance_match:
            boundary = self._boundary(
                step_index=len(self.timeline) + 1,
                label=label,
                intervention=Intervention(baseline=baseline, twin=twin),
                baseline_pulse_payload=baseline_payload,
                twin_pulse_payload=twin_payload,
                semantic_match=semantic_match,
                resonance_match=resonance_match,
            )
        self.timeline.append(outcome)
        return outcome, boundary

    def run(self, interventions: list[tuple[Signal, Signal]], *, labels: list[str] | None = None) -> dict[str, Any]:
        """Run paired interventions and preserve the earliest split."""
        self.timeline.clear()
        divergence: dict[str, Any] | None = None

        for index, (baseline, twin) in enumerate(interventions, start=1):
            label = labels[index - 1] if labels and index <= len(labels) else f"intervention-{index}"
            _, boundary = self.step(baseline, twin, label=label)
            if divergence is None and boundary is not None:
                divergence = boundary

        baseline_final = self.baseline_loom.observe("final")
        twin_final = self.twin_loom.observe("final")
        latest = self.timeline[-1] if self.timeline else {
            "baseline": self.origin_baseline.payload(),
            "twin": self.origin_twin.payload(),
            "baseline_state_snapshot": self.baseline_hub.state_core.snapshot(),
            "twin_state_snapshot": self.twin_hub.state_core.snapshot(),
            "state_delta": [],
        }
        forensics = diagnose_divergence(
            baseline_state=self.baseline_hub.state_core.raw,
            twin_state=self.twin_hub.state_core.raw,
            baseline_status={
                field: latest["baseline"][field]
                for field in ("chaos", "mood", "mesh_events", "reactor_events", "state_keys")
            },
            twin_status={
                field: latest["twin"][field]
                for field in ("chaos", "mood", "mesh_events", "reactor_events", "state_keys")
            },
            baseline_signature=latest["baseline"]["signature"],
            twin_signature=latest["twin"]["signature"],
        ).payload()
        report = {
            "experiment": "counterfactual-twin",
            "engine_version": 1,
            "seed": self.seed,
            "origin_signature": self.origin_baseline.signature,
            "intervention_count": len(interventions),
            "divergence": divergence,
            "timeline": self.timeline,
            "forensics": forensics,
            "final": {
                "semantic_match": (
                    self.baseline_hub.state_core.snapshot()
                    == self.twin_hub.state_core.snapshot()
                ),
                "resonance_match": baseline_final.signature == twin_final.signature,
                "distance": self._distance(baseline_final.signature, twin_final.signature),
            },
        }
        canonical = json.dumps(report, sort_keys=True, separators=(",", ":"))
        report["report_hash"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a counterfactual twin experiment")
    parser.add_argument("--seed", type=int, default=None)
    commands = parser.add_subparsers(dest="command", required=True)
    twin = commands.add_parser("twin", help="run paired realities")
    twin.add_argument("--output", type=Path, required=True)
    twin.add_argument("--spec", type=Path, help="JSON intervention specification")
    twin.add_argument("--agent", help="single-intervention agent id")
    twin.add_argument("--baseline-valence", type=float, default=0.0)
    twin.add_argument("--baseline-arousal", type=float, default=0.5)
    twin.add_argument("--twin-valence", type=float, default=0.0)
    twin.add_argument("--twin-arousal", type=float, default=0.5)
    twin.add_argument("--label", default="cli-split")
    return parser


def _interventions_from_spec(path: Path) -> list[tuple[Signal, Signal]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    pairs: list[tuple[Signal, Signal]] = []
    for item in payload.get("interventions", []):
        baseline = Signal(
            agent_id=item["agent"],
            valence=float(item["baseline"]["valence"]),
            arousal=float(item["baseline"]["arousal"]),
        )
        twin = Signal(
            agent_id=item["agent"],
            valence=float(item["twin"]["valence"]),
            arousal=float(item["twin"]["arousal"]),
        )
        pairs.append((baseline, twin))
    if not pairs:
        raise ValueError("specification contains no interventions")
    return pairs


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "twin":
            if args.spec:
                interventions = _interventions_from_spec(args.spec)
            elif args.agent:
                interventions = [(
                    Signal(args.agent, args.baseline_valence, args.baseline_arousal),
                    Signal(args.agent, args.twin_valence, args.twin_arousal),
                )]
            else:
                raise ValueError("twin requires --spec or --agent")
            report = CounterfactualTwin(seed=args.seed).run(interventions)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            rendered = json.dumps(report, sort_keys=True, indent=2) + "\n"
            _atomic_write(args.output, rendered)
            print(json.dumps({
                "output": str(args.output),
                "report_hash": report["report_hash"],
                "divergence": report["divergence"],
            }, sort_keys=True))
            return 0
    except (OSError, ValueError, json.JSONDecodeError, KeyError) as error:
        print(json.dumps({"error": str(error)}, sort_keys=True))
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
