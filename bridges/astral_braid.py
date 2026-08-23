"""Astral Braid Conservatory — rehearse rituals before they touch reality.

Each MYCELIUM dream expands into shadow timelines. A timeline is only a
reversible proposal: it can be inspected, ranked, quarantined, or rolled back.
Nothing here mutates the source dream or the living substrate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from bridges.chrono_mycelium import AstralTranscript, load_dream, stable_sigil
from mycelium.cognition.dream_compiler import DreamExperiment


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ConsentContract:
    """An explicit boundary for every rehearsal candidate."""

    maximum_entropy: float = 0.85
    maximum_steps: int = 24
    minimum_confidence: float = 0.35
    forbidden_terms: tuple[str, ...] = ("without consent", "override consent")

    def payload(self) -> dict[str, Any]:
        return {
            "maximum_entropy": self.maximum_entropy,
            "maximum_steps": self.maximum_steps,
            "minimum_confidence": self.minimum_confidence,
            "forbidden_terms": list(self.forbidden_terms),
        }


@dataclass(frozen=True)
class ShadowCapsule:
    """A reversible mutation of one dream experiment."""

    strategy: str
    dream: DreamExperiment
    origin_payload: dict[str, Any]

    def rollback(self) -> DreamExperiment:
        raw = self.origin_payload
        return DreamExperiment(
            dream_id=str(raw["dream_id"]),
            hypothesis=str(raw["hypothesis"]),
            genome={key: float(value) for key, value in raw["genome"].items()},
            entropy_budget=float(raw["entropy_budget"]),
            recommended_steps=int(raw["recommended_steps"]),
            confidence=float(raw["confidence"]),
            evidence_hash=str(raw["evidence_hash"]),
        )


class AstralBraidConservatory:
    """Generate, rank, and promote safe shadow timelines."""

    strategies = ("conservative", "lateral", "paradox")

    def __init__(
        self,
        transcript: AstralTranscript,
        contract: ConsentContract | None = None,
        *,
        clock: Callable[[], str] = utc_now,
    ) -> None:
        self.transcript = transcript
        self.contract = contract or ConsentContract()
        self.clock = clock

    def _mutate(self, dream: DreamExperiment, strategy: str) -> DreamExperiment:
        entropy = dream.entropy_budget
        confidence = dream.confidence
        steps = dream.recommended_steps

        if strategy == "conservative":
            genome = {
                key: max(0.0, min(1.0, value * 0.88))
                for key, value in dream.genome.items()
            }
            entropy *= 0.78
            confidence = min(1.0, confidence + 0.04)
        elif strategy == "lateral":
            shifted = {
                key: (value + 0.17) % 1.08
                for key, value in dream.genome.items()
            }
            genome = {key: max(0.0, min(1.0, value)) for key, value in shifted.items()}
            entropy = min(1.0, entropy * 1.02 + 0.03)
        elif strategy == "paradox":
            genome = {
                key: max(0.0, min(1.0, 1.0 - abs(value)))
                for key, value in dream.genome.items()
            }
            entropy = min(1.0, entropy * 1.14)
            confidence *= 0.9
            steps += 1
        else:
            raise ValueError(f"unknown braid strategy: {strategy}")

        return DreamExperiment(
            dream_id=f"{dream.dream_id}:{strategy}",
            hypothesis=dream.hypothesis,
            genome=genome,
            entropy_budget=max(0.0, min(1.0, entropy)),
            recommended_steps=max(1, steps),
            confidence=max(0.0, min(1.0, confidence)),
            evidence_hash=dream.evidence_hash,
        )

    def _evaluate(self, capsule: ShadowCapsule) -> dict[str, Any]:
        dream = capsule.dream
        violations: list[str] = []
        lowered = dream.hypothesis.lower()
        if any(term in lowered for term in self.contract.forbidden_terms):
            violations.append("consent_language")
        if dream.entropy_budget > self.contract.maximum_entropy:
            violations.append("entropy_budget")
        if dream.recommended_steps > self.contract.maximum_steps:
            violations.append("step_budget")
        if dream.confidence < self.contract.minimum_confidence:
            violations.append("confidence_floor")

        average_genome = math.fsum(dream.genome.values()) / max(1, len(dream.genome))
        step_fit = 1.0 - abs(dream.recommended_steps - 12) / 24.0
        score = (
            0.42 * dream.confidence
            + 0.28 * (1.0 - dream.entropy_budget)
            + 0.18 * max(0.0, min(1.0, step_fit))
            + 0.12 * average_genome
        )
        score -= 0.65 * len(violations)

        candidate = {
            "strategy": capsule.strategy,
            "braid_sigil": stable_sigil(f"braid:{dream.dream_id}"),
            "hypothesis": dream.hypothesis,
            "genome": dream.genome,
            "entropy_budget": round(dream.entropy_budget, 6),
            "recommended_steps": dream.recommended_steps,
            "confidence": round(dream.confidence, 6),
            "score": round(score, 6),
            "violations": violations,
            "candidate_hash": "",
        }
        candidate["candidate_hash"] = canonical_hash(candidate)
        return candidate

    def braid(self, dream: DreamExperiment) -> dict[str, Any]:
        candidates: list[dict[str, Any]] = []
        for strategy in self.strategies:
            capsule = ShadowCapsule(strategy, self._mutate(dream, strategy), dream.payload())
            candidate = self._evaluate(capsule)
            candidates.append(candidate)
            self.transcript.send("braid.shadow", {"strategy": strategy, "candidate": candidate})

        viable = [item for item in candidates if not item["violations"]]
        selected = (
            max(viable, key=lambda item: (item["score"], item["candidate_hash"]))
            if viable else None
        )
        if selected is None:
            emitted = [self.transcript.send("braid.quarantined", {"reason": "no_viable_timeline"})]
        else:
            emitted = [self.transcript.send("braid.promoted", {"selected": selected})]

        report = {
            "experiment": "astral-braid-conservatory",
            "engine_version": 1,
            "source_dream_id": dream.dream_id,
            "source_evidence_hash": dream.evidence_hash,
            "contract": self.contract.payload(),
            "candidates": candidates,
            "selected_strategy": selected["strategy"] if selected else None,
            "selected_braid_sigil": selected["braid_sigil"] if selected else None,
            "topics": [record["topic"] for record in emitted],
            "emitted": emitted,
            "performed_at": self.clock(),
        }
        stable_report = {
            key: value for key, value in report.items()
            if key not in ("performed_at", "emitted")
        }
        report["certificate_hash"] = canonical_hash(stable_report)
        return report

    @staticmethod
    def capsule_for(report: dict[str, Any], source: DreamExperiment, strategy: str) -> ShadowCapsule:
        if strategy not in AstralBraidConservatory.strategies:
            raise ValueError(f"unknown braid strategy: {strategy}")
        present = any(item["strategy"] == strategy for item in report["candidates"])
        if not present:
            raise ValueError("report does not contain the requested strategy")
        helper = AstralBraidConservatory(AstralTranscript(Path("/tmp/astral-braid-unused.jsonl")))
        return ShadowCapsule(strategy, helper._mutate(source, strategy), source.payload())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Rehearse MYCELIUM dreams as reversible braids")
    parser.add_argument("--dream-file", type=Path, default=None)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--steps", type=int, default=10)
    parser.add_argument("--sites", type=int, default=7)
    parser.add_argument("--transcript", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.dream_file:
            dream = load_dream(args.dream_file)
        else:
            from mycelium.cognition.dream_compiler import DreamCompiler, build_demo_network

            compiled = DreamCompiler().compile(build_demo_network(args.seed, args.steps, args.sites))
            if compiled is None:
                raise ValueError("no lived events were available to compile into a dream")
            dream = compiled

        report = AstralBraidConservatory(AstralTranscript(args.transcript)).braid(dream)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, sort_keys=True))
        return 0
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 1
