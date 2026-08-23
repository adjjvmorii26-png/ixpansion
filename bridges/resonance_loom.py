"""Resonance Loom — deterministic cross-engine telemetry.

The Loom folds signals from ``omega_prime``, ``omega_fractal_engine``, and
``project_root`` into stable pulses. Identical engine states therefore produce
identical signatures, making emergent behavior comparable across machines.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import tempfile
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from bridges.bridge_core import BridgeHub

_PULSE_FIELDS = {
    "tick": int,
    "label": str,
    "chaos": float,
    "mood": str,
    "state_keys": int,
    "reactor_events": int,
    "mesh_events": int,
    "signature": str,
}


def _atomic_write(path: Path, text: str) -> None:
    """Replace ``path`` atomically and flush the containing directory."""
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temporary.unlink(missing_ok=True)


@dataclass(frozen=True)
class ResonancePulse:
    """A replayable observation of the combined engines."""

    tick: int
    label: str
    chaos: float
    mood: str
    state_keys: int
    reactor_events: int
    mesh_events: int
    signature: str

    @property
    def short_signature(self) -> str:
        return self.signature[:12]

    def payload(self) -> dict[str, Any]:
        value = asdict(self)
        value["short_signature"] = self.short_signature
        return value

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "ResonancePulse":
        missing = sorted(set(_PULSE_FIELDS) - set(payload))
        if missing:
            raise ValueError(f"resonance pulse missing fields: {', '.join(missing)}")
        converted = {
            field: caster(payload[field]) for field, caster in _PULSE_FIELDS.items()
        }
        return cls(**converted)


class ResonanceLoom:
    """Weave engine state into an auditable telemetry stream."""

    def __init__(self, hub: BridgeHub | None = None, seed: int | None = None) -> None:
        self.hub = hub if hub is not None else BridgeHub(seed=seed)
        self.tick = 0

    def weave(
        self,
        agent_id: str,
        valence: float,
        arousal: float,
        *,
        event_layer: str = "meta",
    ) -> dict[str, Any]:
        """Push one agent signal through state, mood, mesh, and reactor paths."""
        self.hub.set_state(agent_id, {"valence": valence, "arousal": arousal})
        mood = self.hub.propagate_emotion(agent_id)
        deliveries = self.hub.route_event(
            event_layer,
            "resonance_weave",
            {"agent_id": agent_id, "valence": valence, "arousal": arousal},
        )
        return {
            "agent_id": agent_id,
            "mood": mood,
            "deliveries": deliveries,
            "chaos": self.hub.get_chaos_level(),
        }

    def observe(self, label: str = "heartbeat") -> ResonancePulse:
        """Capture a deterministic fingerprint of all connected engines."""
        self.tick += 1
        status = self.hub.status
        canonical = json.dumps(
            {
                "chaos": status["chaos"],
                "mood": status["mood"],
                "mesh_events": status["mesh_events"],
                "reactor_events": status["reactor_events"],
                "state_keys": status["state_keys"],
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return ResonancePulse(
            tick=self.tick,
            label=label,
            chaos=float(status["chaos"]),
            mood=str(status["mood"]),
            state_keys=int(status["state_keys"]),
            reactor_events=int(status["reactor_events"]),
            mesh_events=int(status["mesh_events"]),
            signature=digest,
        )

    def persist(self, path: str | Path, label: str = "heartbeat") -> ResonancePulse:
        """Append a pulse and publish its latest snapshot under an exclusive lock."""
        pulse = self.observe(label)
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(pulse.payload(), sort_keys=True, separators=(",", ":"))

        with destination.open("a+", encoding="utf-8") as lock_stream:
            fcntl.flock(lock_stream.fileno(), fcntl.LOCK_EX)
            try:
                with destination.open("a", encoding="utf-8") as stream:
                    stream.write(line + "\n")
                    stream.flush()
                    os.fsync(stream.fileno())
                _atomic_write(destination.with_name(destination.name + ".latest"), line + "\n")
            finally:
                fcntl.flock(lock_stream.fileno(), fcntl.LOCK_UN)
        return pulse

    @staticmethod
    def load(path: str | Path, *, strict: bool = False) -> list[dict[str, Any]]:
        """Read JSONL pulses; optionally reject any malformed record."""
        pulses: list[dict[str, Any]] = []
        try:
            lines = Path(path).read_text(encoding="utf-8").splitlines()
        except FileNotFoundError:
            if strict:
                raise
            return pulses

        for line_number, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            try:
                pulses.append(json.loads(line))
            except json.JSONDecodeError as error:
                if strict:
                    raise ValueError(
                        f"invalid resonance JSON at {path}:{line_number}"
                    ) from error
        return pulses


@dataclass(frozen=True)
class ResonanceVerdict:
    """A compact comparison between two engine pulses."""

    old_signature: str
    new_signature: str
    distance: int
    similarity: float
    verdict: str
    changed_fields: tuple[str, ...]

    def payload(self) -> dict[str, Any]:
        value = asdict(self)
        value["changed_fields"] = list(self.changed_fields)
        return value


class PulseOracle:
    """Detect repetition, drift, mutations, and attractors in resonance time."""

    STABLE_DISTANCE = 8
    SHIFTING_DISTANCE = 32
    _STATUS_FIELDS = ("chaos", "mood", "mesh_events", "reactor_events", "state_keys")

    def __init__(self) -> None:
        self.history: list[ResonancePulse] = []
        self._seen: set[str] = set()

    @staticmethod
    def _distance(old: str, new: str) -> int:
        return sum(a != b for a, b in zip(old, new)) + abs(len(old) - len(new))

    @classmethod
    def _verdict(cls, distance: int, repeated: bool) -> str:
        if repeated:
            return "recurrence"
        if distance == 0:
            return "identical"
        if distance <= cls.STABLE_DISTANCE:
            return "stable"
        if distance <= cls.SHIFTING_DISTANCE:
            return "shifting"
        return "mutation"

    @classmethod
    def _status(cls, pulse: ResonancePulse) -> dict[str, Any]:
        return {
            "chaos": pulse.chaos,
            "mood": pulse.mood,
            "mesh_events": pulse.mesh_events,
            "reactor_events": pulse.reactor_events,
            "state_keys": pulse.state_keys,
        }

    def record(self, pulse: ResonancePulse) -> ResonanceVerdict:
        previous = self.history[-1] if self.history else None
        repeated = pulse.signature in self._seen
        if previous is None:
            distance, changed, verdict = 0, (), "baseline"
        else:
            distance = self._distance(previous.signature, pulse.signature)
            old_status, new_status = self._status(previous), self._status(pulse)
            changed = tuple(
                field for field in self._STATUS_FIELDS if old_status[field] != new_status[field]
            )
            verdict = self._verdict(distance, repeated)

        self.history.append(pulse)
        self._seen.add(pulse.signature)
        similarity = max(0.0, round(1.0 - distance / 64, 4))
        return ResonanceVerdict(
            old_signature=previous.signature if previous else pulse.signature,
            new_signature=pulse.signature,
            distance=distance,
            similarity=similarity,
            verdict=verdict,
            changed_fields=changed,
        )

    @property
    def attractors(self) -> int:
        """Number of distinct states encountered by this oracle."""
        return len(self._seen)

    def compare_journals(self, old_path: str | Path, new_path: str | Path) -> dict[str, Any]:
        """Compare the latest valid records from two JSONL journals."""
        old_pulses = ResonanceLoom.load(old_path)
        new_pulses = ResonanceLoom.load(new_path)
        if not old_pulses or not new_pulses:
            raise ValueError("both resonance journals must contain at least one pulse")
        old, new = old_pulses[-1], new_pulses[-1]
        distance = self._distance(old["signature"], new["signature"])
        changed_fields = sorted(
            field for field in self._STATUS_FIELDS if old.get(field) != new.get(field)
        )
        repeated = old["signature"] == new["signature"]
        return {
            "old_signature": old["signature"],
            "new_signature": new["signature"],
            "distance": distance,
            "similarity": max(0.0, round(1.0 - distance / 64, 4)),
            "verdict": self._verdict(distance, repeated),
            "changed_fields": changed_fields,
        }

    def analyze_journal(self, path: str | Path) -> dict[str, Any]:
        """Build a temporal portrait of recurrence, drift, and attractors."""
        raw_pulses = ResonanceLoom.load(path, strict=True)
        if not raw_pulses:
            raise ValueError("resonance journal is empty")
        pulses = [ResonancePulse.from_payload(record) for record in raw_pulses]
        recorder = PulseOracle()
        trajectory = [verdict.payload() for verdict in map(recorder.record, pulses)]

        signature_counts = Counter(pulse.signature for pulse in pulses)
        transition_counts = Counter(entry["verdict"] for entry in trajectory[1:])
        comparisons = max(len(pulses) - 1, 0)
        attractors = [
            {
                "signature": signature,
                "count": count,
                "ticks": [
                    pulse.tick for pulse in pulses if pulse.signature == signature
                ],
                "cycle_length": (
                    max(pulse.tick for pulse in pulses if pulse.signature == signature)
                    - min(pulse.tick for pulse in pulses if pulse.signature == signature)
                    if count > 1
                    else 0
                ),
            }
            for signature, count in signature_counts.most_common()
            if count > 1
        ]
        similarities = [entry["similarity"] for entry in trajectory[1:]]

        return {
            "pulses": len(pulses),
            "distinct_states": len(signature_counts),
            "attractor_count": len(attractors),
            "attractors": attractors,
            "recurrence_rate": round((len(pulses) - len(signature_counts)) / comparisons, 4)
            if comparisons
            else 0.0,
            "novelty_rate": round((len(signature_counts) - 1) / comparisons, 4)
            if comparisons
            else 0.0,
            "mean_similarity": round(sum(similarities) / len(similarities), 4)
            if similarities
            else 1.0,
            "transitions": dict(sorted(transition_counts.items())),
            "trajectory": trajectory,
            "current_signature": pulses[-1].signature,
            "current_verdict": trajectory[-1]["verdict"],
            "tick_span": max(pulse.tick for pulse in pulses)
            - min(pulse.tick for pulse in pulses),
        }


def build_parser() -> argparse.ArgumentParser:
    """Build the local and CI-facing resonance command line."""
    parser = argparse.ArgumentParser(description="Observe ALEPH resonance pulses")
    parser.add_argument("--seed", type=int, default=None, help="deterministic bridge seed")
    commands = parser.add_subparsers(dest="command", required=True)

    def add_signal_arguments(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("--agent", default=None, help="optional agent signal to weave")
        subparser.add_argument("--valence", type=float, default=0.0)
        subparser.add_argument("--arousal", type=float, default=0.5)

    observe = commands.add_parser("observe", help="print one pulse")
    add_signal_arguments(observe)

    persist = commands.add_parser("persist", help="append one JSONL pulse")
    persist.add_argument("path", type=Path)
    persist.add_argument("--label", default="heartbeat")
    add_signal_arguments(persist)

    analyze = commands.add_parser("analyze", help="summarize a resonance journal")
    analyze.add_argument("path", type=Path)

    compare = commands.add_parser("compare", help="compare latest journal pulses")
    compare.add_argument("old", type=Path)
    compare.add_argument("new", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    loom = ResonanceLoom(seed=args.seed)
    try:
        if args.command == "observe":
            if args.agent:
                loom.weave(args.agent, args.valence, args.arousal)
            result: Any = loom.observe().payload()
        elif args.command == "persist":
            if args.agent:
                loom.weave(args.agent, args.valence, args.arousal)
            result = loom.persist(args.path, args.label).payload()
        elif args.command == "analyze":
            result = PulseOracle().analyze_journal(args.path)
        else:
            result = PulseOracle().compare_journals(args.old, args.new)
    except (OSError, ValueError) as error:
        print(json.dumps({"error": str(error)}, sort_keys=True))
        return 2

    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
