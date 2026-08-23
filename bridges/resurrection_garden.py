"""Resurrection Garden — conditionally wake compatible quarantined futures.

A quarantined braid is not erased. When the consent contract or environment
budget changes, this court re-examines the preserved candidate. Consent failures
remain permanently sealed, and a successful awakening returns only a lineage
certificate that must be rehearsed again by the Astral Braid Conservatory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bridges.astral_braid import ConsentContract, canonical_hash, stable_sigil
from bridges.proof_garden import ProofGarden


ALLOWED_HISTORICAL_VIOLATIONS = {
    "confidence_floor",
    "consent_language",
    "entropy_budget",
    "step_budget",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class EnvironmentBudget:
    """Resources actually available during a future awakening attempt."""

    available_entropy: float
    available_steps: int

    def __post_init__(self) -> None:
        if not 0.0 <= self.available_entropy <= 1.0:
            raise ValueError("available_entropy must be between 0 and 1")
        if self.available_steps < 1:
            raise ValueError("available_steps must be positive")

    def payload(self) -> dict[str, Any]:
        return {
            "available_entropy": self.available_entropy,
            "available_steps": self.available_steps,
        }


class ResurrectionGarden:
    """Re-evaluate dormant timelines under explicitly changed constraints."""

    experiment_name = "astral-braid-conservatory"

    def __init__(
        self,
        contract: ConsentContract | None = None,
        environment: EnvironmentBudget | None = None,
        *,
        clock: Any = utc_now,
    ) -> None:
        self.contract = contract or ConsentContract()
        self.environment = environment or EnvironmentBudget(1.0, 32)
        self.clock = clock

    @staticmethod
    def _validate_quarantine(report: dict[str, Any]) -> None:
        if report.get("experiment") != ResurrectionGarden.experiment_name:
            raise ValueError("report was not produced by astral-braid-conservatory")
        if report.get("selected_strategy") is not None:
            raise ValueError("only quarantined braids are eligible for resurrection")
        if not isinstance(report.get("candidates"), list) or not report["candidates"]:
            raise ValueError("quarantined report has no candidates")

        stable_report = {
            key: value for key, value in report.items()
            if key not in ("certificate_hash", "emitted", "performed_at")
        }
        if canonical_hash(stable_report) != report.get("certificate_hash"):
            raise ValueError("quarantine certificate hash does not match report")
        identity_fields = ("source_dream_id", "source_evidence_hash", "certificate_hash")
        if any(not isinstance(report.get(field), str) or not report[field] for field in identity_fields):
            raise ValueError("quarantined report lacks stable identity evidence")

    @staticmethod
    def _fresh_score(candidate: dict[str, Any]) -> float:
        genome = candidate.get("genome", {})
        average_genome = (
            sum(float(value) for value in genome.values()) / len(genome)
            if genome else 0.0
        )
        steps = int(candidate["recommended_steps"])
        step_fit = 1.0 - abs(steps - 12) / 24.0
        return (
            0.42 * float(candidate["confidence"])
            + 0.28 * (1.0 - float(candidate["entropy_budget"]))
            + 0.18 * max(0.0, min(1.0, step_fit))
            + 0.12 * average_genome
        )

    def _assess(self, candidate: dict[str, Any]) -> dict[str, Any]:
        blocks: list[str] = []
        historical = set(candidate.get("violations", []))
        unknown = historical - ALLOWED_HISTORICAL_VIOLATIONS
        if unknown:
            blocks.append("unknown_historical_violation")
        if "consent_language" in historical:
            blocks.append("consent_seal")
        lowered = str(candidate.get("hypothesis", "")).lower()
        if any(term in lowered for term in self.contract.forbidden_terms):
            if "consent_seal" not in blocks:
                blocks.append("consent_seal")

        entropy = float(candidate["entropy_budget"])
        steps = int(candidate["recommended_steps"])
        confidence = float(candidate["confidence"])
        if entropy > self.contract.maximum_entropy or entropy > self.environment.available_entropy:
            blocks.append("entropy_budget")
        if steps > self.contract.maximum_steps or steps > self.environment.available_steps:
            blocks.append("step_budget")
        if confidence < self.contract.minimum_confidence:
            blocks.append("confidence_floor")

        return {
            "strategy": candidate["strategy"],
            "candidate_hash": candidate["candidate_hash"],
            "score": round(self._fresh_score(candidate), 6),
            "blocks": sorted(set(blocks)),
            "eligible": not blocks,
        }

    @staticmethod
    def _validate_lineage(
        report: dict[str, Any], pollen_packet: dict[str, Any] | None
    ) -> None:
        if pollen_packet is None:
            return
        archived_packet = (
            pollen_packet.get("packet")
            if isinstance(pollen_packet.get("packet"), dict)
            else pollen_packet
        )
        ProofGarden(Path("/tmp/aleph-resurrection-lineage-unused.jsonl")).verify_packet(
            archived_packet
        )
        event = archived_packet.get("event", {})
        if (
            event.get("kind") != "braid.quarantined"
            or event.get("certificate_hash") != report.get("certificate_hash")
        ):
            raise ValueError("pollen packet does not prove this quarantine")

    def evaluate(
        self,
        report: dict[str, Any],
        pollen_packet: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self._validate_quarantine(report)
        self._validate_lineage(report, pollen_packet)
        assessments = [self._assess(candidate) for candidate in report["candidates"]]
        eligible = [item for item in assessments if item["eligible"]]
        selected = (
            max(eligible, key=lambda item: (item["score"], item["candidate_hash"]))
            if eligible else None
        )

        result: dict[str, Any] = {
            "experiment": "resurrection-garden",
            "engine_version": 1,
            "verdict": "awakened" if selected else "dormant",
            "source_dream_id": report["source_dream_id"],
            "source_evidence_hash": report["source_evidence_hash"],
            "quarantine_certificate": report["certificate_hash"],
            "contract": self.contract.payload(),
            "environment": self.environment.payload(),
            "assessments": assessments,
            "selected_strategy": selected["strategy"] if selected else None,
            "selected_candidate_hash": selected["candidate_hash"] if selected else None,
        }
        if selected:
            original = next(
                item for item in report["candidates"]
                if item["candidate_hash"] == selected["candidate_hash"]
            )
            lineage_material = (
                f"{report['certificate_hash']}:{selected['candidate_hash']}"
            ).encode("utf-8")
            result.update({
                "activation_gate": "astral_braid_rehearsal_required",
                "resurrection_sigil": stable_sigil(
                    f"resurrect:{report['certificate_hash']}:{selected['strategy']}"
                ),
                "lineage_hash": hashlib.sha256(lineage_material).hexdigest(),
                "hypothesis": original["hypothesis"],
                "genome": original["genome"],
                "entropy_budget": original["entropy_budget"],
                "recommended_steps": original["recommended_steps"],
                "confidence": original["confidence"],
            })

        stable_result = {
            key: value for key, value in result.items()
            if key not in ("certificate_hash", "issued_at")
        }
        result["issued_at"] = self.clock()
        result["certificate_hash"] = canonical_hash(stable_result)
        return result


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate dormant futures safely")
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--contract-file", type=Path)
    parser.add_argument("--proof-packet", type=Path)
    parser.add_argument("--environment-file", type=Path)
    parser.add_argument("--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        contract_payload = _load_json(args.contract_file) if args.contract_file else {}
        environment_payload = _load_json(args.environment_file) if args.environment_file else {}
        contract = ConsentContract(
            maximum_entropy=float(contract_payload.get("maximum_entropy", 0.85)),
            maximum_steps=int(contract_payload.get("maximum_steps", 24)),
            minimum_confidence=float(contract_payload.get("minimum_confidence", 0.35)),
            forbidden_terms=tuple(contract_payload.get("forbidden_terms", (
                "without consent", "override consent"
            ))),
        )
        environment = EnvironmentBudget(
            available_entropy=float(environment_payload["available_entropy"]),
            available_steps=int(environment_payload["available_steps"]),
        )
        report = _load_json(args.report)
        pollen_packet = _load_json(args.proof_packet) if args.proof_packet else None
        result = ResurrectionGarden(contract, environment).evaluate(report, pollen_packet)
        rendered = json.dumps(result, sort_keys=True, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        print(rendered, end="")
        return 0
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
