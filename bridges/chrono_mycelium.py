"""Chrono-Mycelium Bridge — bind living dreams to Chrono Forge rituals.

This is the seam between two experimental dialects: MYCELIUM supplies lived,
consent-bounded events; Chrono Forge supplies stable HEX sigils, an astral JSONL
bus, and recursion safety. The bridge keeps both vocabularies without allowing
either one to rewrite the other.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mycelium.cognition.dream_compiler import (
    DreamCompiler,
    DreamExperiment,
    build_demo_network,
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def stable_sigil(name: str) -> str:
    """Return the Chrono Forge-compatible eight-digit HEX sigil."""
    digest = hashlib.sha256(name.encode("utf-8")).hexdigest()[:8].upper()
    return f"0x{digest}"


@dataclass(frozen=True)
class SigilRecord:
    name: str
    sigil: str
    source: str
    source_hash: str


@dataclass
class AstralTranscript:
    """Small append-only JSONL bus with an injectable storage location."""

    path: Path
    clock: Callable[[], str] = utc_now

    def send(self, topic: str, payload: dict[str, Any]) -> dict[str, Any]:
        record = {
            "emitted_at": self.clock(),
            "topic": topic,
            "payload": payload,
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
            stream.flush()
        return record

    def tail(self, count: int = 10) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        records: list[dict[str, Any]] = []
        for line in self.path.read_text(encoding="utf-8").splitlines()[-count:]:
            if line.strip():
                records.append(json.loads(line))
        return records


@dataclass
class RecursionAnchor:
    """File-backed depth limiter for generated or self-modifying rituals."""

    path: Path
    maximum_depth: int = 5

    def __post_init__(self) -> None:
        if self.maximum_depth < 1:
            raise ValueError("maximum_depth must be positive")

    def _read(self) -> dict[str, Any]:
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            return {"depth": int(raw.get("depth", 0)), "stack": list(raw.get("stack", []))}
        except (FileNotFoundError, json.JSONDecodeError, TypeError, ValueError):
            return {"depth": 0, "stack": []}

    def enter(self, label: str) -> dict[str, Any]:
        state = self._read()
        depth = state["depth"] + 1
        stack = [*state["stack"], label]
        result = {
            "ok": depth <= self.maximum_depth,
            "depth": depth,
            "maximum_depth": self.maximum_depth,
            "stack": stack,
        }
        if result["ok"]:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps({"depth": depth, "stack": stack}, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        else:
            result["reason"] = "recursion_anchor_trip"
        return result

    def reset(self) -> dict[str, Any]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps({"depth": 0, "stack": []}, sort_keys=True) + "\n", encoding="utf-8"
        )
        return {"ok": True, "depth": 0}


class ChronoMyceliumBridge:
    """Translate a MYCELIUM dream into a safe Chrono Forge ritual."""

    def __init__(
        self,
        transcript: AstralTranscript,
        anchor: RecursionAnchor | None = None,
        *,
        clock: Callable[[], str] = utc_now,
    ) -> None:
        self.transcript = transcript
        self.anchor = anchor or RecursionAnchor(Path("/tmp/aleph-chronomycelium-anchor.json"))
        self.clock = clock

    def _sigil_record(self, name: str, source: str, source_value: Any) -> SigilRecord:
        canonical = json.dumps(source_value, sort_keys=True, separators=(",", ":"), default=str)
        source_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return SigilRecord(name, stable_sigil(name), source, source_hash)

    def ritual(self, dream: DreamExperiment) -> dict[str, Any]:
        dream_sigil = self._sigil_record(f"dream:{dream.dream_id}", "dream_experiment", dream.payload())
        anchor_result = self.anchor.enter(f"dream:{dream.dream_id}")
        emitted: list[dict[str, Any]] = []

        try:
            if not anchor_result["ok"]:
                emitted.append(self.transcript.send("ritual.blocked", {
                    "reason": anchor_result["reason"],
                    "depth": anchor_result["depth"],
                    "dream_sigil": dream_sigil.sigil,
                }))
            else:
                emitted.append(self.transcript.send("dream.sigil", {
                    **asdict(dream_sigil),
                    "hypothesis": dream.hypothesis,
                    "confidence": dream.confidence,
                }))
                emitted.append(self.transcript.send("dream.invocation", {
                    "entropy_budget": dream.entropy_budget,
                    "genome": dream.genome,
                    "recommended_steps": dream.recommended_steps,
                }))

            report = {
                "experiment": "chrono-mycelium-bridge",
                "engine_version": 1,
                "dream_id": dream.dream_id,
                "dream_sigil": dream_sigil.sigil,
                "source_hash": dream_sigil.source_hash,
                "anchor": anchor_result,
                "topics": [record["topic"] for record in emitted],
                "emitted": emitted,
                "performed_at": self.clock(),
            }
            canonical = json.dumps({
                key: value for key, value in report.items() if key != "performed_at"
            }, sort_keys=True, separators=(",", ":"))
            report["evidence_hash"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
            return report
        finally:
            if anchor_result.get("ok"):
                self.anchor.reset()


def load_dream(path: Path) -> DreamExperiment:
    raw = json.loads(path.read_text(encoding="utf-8")).get("dream")
    if not isinstance(raw, dict):
        raise ValueError("dream artifact does not contain a dream object")
    return DreamExperiment(
        dream_id=str(raw["dream_id"]),
        hypothesis=str(raw["hypothesis"]),
        genome={key: float(value) for key, value in raw["genome"].items()},
        entropy_budget=float(raw["entropy_budget"]),
        recommended_steps=int(raw["recommended_steps"]),
        confidence=float(raw["confidence"]),
        evidence_hash=str(raw["evidence_hash"]),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bind MYCELIUM dreams to Chrono Forge")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--steps", type=int, default=10)
    parser.add_argument("--sites", type=int, default=7)
    parser.add_argument("--dream-file", type=Path, default=None)
    parser.add_argument("--transcript", type=Path, required=True)
    parser.add_argument("--anchor-state", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        dream = load_dream(args.dream_file) if args.dream_file else (
            DreamCompiler().compile(build_demo_network(args.seed, args.steps, args.sites))
        )
        if dream is None:
            raise ValueError("no lived events were available to compile into a dream")
        bridge = ChronoMyceliumBridge(
            AstralTranscript(args.transcript),
            RecursionAnchor(args.anchor_state),
        )
        report = bridge.ritual(dream)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({
            "output": str(args.output),
            "dream_sigil": report["dream_sigil"],
            "topics": report["topics"],
            "evidence_hash": report["evidence_hash"],
        }, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        print(json.dumps({"error": str(error)}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
