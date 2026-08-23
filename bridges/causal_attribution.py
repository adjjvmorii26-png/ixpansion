"""Causal Attribution — classify interventions by controlled replay.

For every paired intervention, ALEPH runs three worlds:

1. **Observed**: the original counterfactual sequence.
2. **Ablated**: that intervention is made identical across realities.
3. **Isolated**: only that intervention differs across realities.

Comparing those outcomes separates direct causes, required catalysts,
independent triggers, alternative routes, and contextual synergies.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from bridges.counterfactual_twin import (
    CounterfactualTwin,
    Signal,
    load_interventions,
)
from bridges.resonance_loom import _atomic_write


@dataclass(frozen=True)
class CausalVerdict:
    """Replay-derived causal role for one intervention."""

    intervention_index: int
    label: str
    classification: str
    necessary: bool
    sufficient: bool
    causal_mass: float
    full_diverged: bool
    ablated_diverged: bool
    solo_diverged: bool
    full_first_kind: str
    ablated_first_kind: str
    solo_first_kind: str
    changed_path_overlap: float

    def payload(self) -> dict[str, Any]:
        return asdict(self)


class CausalAttributor:
    """Attribute observed divergence through deterministic world replay."""

    def __init__(self, seed: int | None = None, *, target: str = "semantic") -> None:
        if target not in {"semantic", "resonance"}:
            raise ValueError("target must be 'semantic' or 'resonance'")
        self.seed = seed
        self.target = target

    @staticmethod
    def _first_kind(report: dict[str, Any]) -> str:
        divergence = report.get("divergence")
        return divergence["kind"] if divergence else "none"

    def _diverged(self, report: dict[str, Any]) -> bool:
        final = report["final"]
        field = "semantic_match" if self.target == "semantic" else "resonance_match"
        return final[field] is False

    @staticmethod
    def _changed_paths(report: dict[str, Any]) -> set[str]:
        divergence = report.get("divergence") or {}
        return set(divergence.get("changed_paths", []))

    @staticmethod
    def _overlap(left: set[str], right: set[str]) -> float:
        union = left | right
        return round(len(left & right) / len(union), 6) if union else 1.0

    def run(
        self,
        interventions: list[tuple[Signal, Signal]],
        *,
        labels: list[str] | None = None,
    ) -> dict[str, Any]:
        """Run all control worlds and derive one verdict per intervention."""
        full_twin = CounterfactualTwin(seed=self.seed)
        full_report = full_twin.run(interventions, labels=labels)
        full_diverged = self._diverged(full_report)

        verdicts: list[dict[str, Any]] = []
        for index, pair in enumerate(interventions):
            baseline_signal = pair[0]
            ablated_pairs = list(interventions)
            ablated_pairs[index] = (baseline_signal, baseline_signal)
            ablated_report = CounterfactualTwin(seed=self.seed).run(
                ablated_pairs, labels=labels
            )

            solo_pairs = [
                (pair[0], pair[0]) for pair in interventions
            ]
            solo_pairs[index] = (interventions[index][0], interventions[index][1])

            solo_report = CounterfactualTwin(seed=self.seed).run(solo_pairs, labels=labels)
            ablated_diverged = self._diverged(ablated_report)
            solo_diverged = self._diverged(solo_report)

            necessary = full_diverged and not ablated_diverged
            sufficient = solo_diverged
            if not full_diverged:
                classification = "dormant_potential"
            elif necessary and sufficient:
                classification = "direct_cause"
            elif necessary:
                classification = "required_catalyst"
            elif sufficient and ablated_diverged:
                classification = "alternative_route"
            elif sufficient:
                classification = "independent_trigger"
            else:
                classification = "contextual_synergist"

            full_paths = self._changed_paths(full_report)
            solo_paths = self._changed_paths(solo_report)
            causal_mass = round((int(necessary) + int(sufficient)) / 2, 6)
            label = labels[index] if labels and index < len(labels) else f"intervention-{index + 1}"
            verdict = CausalVerdict(
                intervention_index=index + 1,
                label=label,
                classification=classification,
                necessary=necessary,
                sufficient=sufficient,
                causal_mass=causal_mass,
                full_diverged=full_diverged,
                ablated_diverged=ablated_diverged,
                solo_diverged=solo_diverged,
                full_first_kind=self._first_kind(full_report),
                ablated_first_kind=self._first_kind(ablated_report),
                solo_first_kind=self._first_kind(solo_report),
                changed_path_overlap=self._overlap(full_paths, solo_paths),
            )
            verdicts.append(verdict.payload())

        fingerprint_inputs = {
            "seed": self.seed,
            "target": self.target,
            "verdicts": [
                {
                    "index": item["intervention_index"],
                    "classification": item["classification"],
                    "full_kind": item["full_first_kind"],
                    "ablated_kind": item["ablated_first_kind"],
                    "solo_kind": item["solo_first_kind"],
                }
                for item in verdicts
            ],
        }
        canonical = json.dumps(fingerprint_inputs, sort_keys=True, separators=(",", ":"))
        report = {
            "experiment": "causal-attribution",
            "engine_version": 1,
            "seed": self.seed,
            "target": self.target,
            "intervention_count": len(interventions),
            "observed_target_diverged": full_diverged,
            "observed_first_kind": self._first_kind(full_report),
            "verdicts": verdicts,
            "causal_fingerprint": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
            "full_counterfactual": full_report,
        }
        report_hash = hashlib.sha256(
            json.dumps(report, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        report["report_hash"] = report_hash
        return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Attribute counterfactual causality")
    parser.add_argument("--seed", type=int, default=None)
    commands = parser.add_subparsers(dest="command", required=True)
    attribute = commands.add_parser("attribute", help="attribute intervention effects")
    attribute.add_argument("--spec", type=Path, required=True)
    attribute.add_argument("--output", type=Path, required=True)
    attribute.add_argument("--target", choices=("semantic", "resonance"), default="semantic")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        interventions = load_interventions(args.spec)
        if not interventions:
            raise ValueError("specification contains no interventions")
        report = CausalAttributor(seed=args.seed, target=args.target).run(interventions)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        rendered = json.dumps(report, sort_keys=True, indent=2) + "\n"
        _atomic_write(args.output, rendered)
        print(json.dumps({
            "output": str(args.output),
            "report_hash": report["report_hash"],
            "causal_fingerprint": report["causal_fingerprint"],
            "verdicts": [
                {key: item[key] for key in ("label", "classification", "causal_mass")}
                for item in report["verdicts"]
            ],
        }, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(json.dumps({"error": str(error)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
