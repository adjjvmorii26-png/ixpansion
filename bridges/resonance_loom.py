"""Resonance Loom — deterministic cross-engine telemetry.

The Loom folds signals from ``omega_prime``, ``omega_fractal_engine``,
``project_root``, and the Nexus Observatory into one stable pulse.  The pulse is
deliberately reproducible: identical engine states produce identical signatures,
which makes emergent behavior comparable across machines and CI runs.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from bridges.bridge_core import BridgeHub


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
        """Append one pulse as JSONL and atomically expose the latest snapshot."""
        pulse = self.observe(label)
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(pulse.payload(), sort_keys=True, separators=(",", ":"))
        with destination.open("a", encoding="utf-8") as stream:
            stream.write(line + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        latest = destination.with_name(destination.name + ".latest")
        latest.write_text(line + "\n", encoding="utf-8")
        return pulse

    @staticmethod
    def load(path: str | Path) -> list[dict[str, Any]]:
        """Read a pulse journal, ignoring blank/corrupt trailing records."""
        pulses: list[dict[str, Any]] = []
        try:
            lines = Path(path).read_text(encoding="utf-8").splitlines()
        except FileNotFoundError:
            return pulses
        for line in lines:
            if not line.strip():
                continue
            try:
                pulses.append(json.loads(line))
            except json.JSONDecodeError:
                continue
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
    """Detect repetition, drift, and attractors across resonance pulses.

    Two identical states are a *recurrence*. Small hexadecimal divergence is
    stability; broad divergence is mutation. The exact thresholds are public so
    experiments remain reproducible and comparable.
    """

    STABLE_DISTANCE = 8
    SHIFTING_DISTANCE = 32

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

    def record(self, pulse: ResonancePulse) -> ResonanceVerdict:
        previous = self.history[-1] if self.history else None
        repeated = pulse.signature in self._seen
        if previous is None:
            distance, changed = 0, ()
            verdict = "baseline"
        else:
            distance = self._distance(previous.signature, pulse.signature)
            fields = (
                "chaos", "mood", "mesh_events", "reactor_events", "state_keys",
            )
            old_status = {
                "chaos": previous.chaos,
                "mood": previous.mood,
                "mesh_events": previous.mesh_events,
                "reactor_events": previous.reactor_events,
                "state_keys": previous.state_keys,
            }
            new_status = {
                "chaos": pulse.chaos,
                "mood": pulse.mood,
                "mesh_events": pulse.mesh_events,
                "reactor_events": pulse.reactor_events,
                "state_keys": pulse.state_keys,
            }
            changed = tuple(field for field in fields if old_status[field] != new_status[field])
            verdict = self._verdict(distance, repeated)

        self.history.append(pulse)
        self._seen.add(pulse.signature)
        similarity = 1.0 - (distance / 64 if distance else 0.0)
        return ResonanceVerdict(
            old_signature=previous.signature if previous else pulse.signature,
            new_signature=pulse.signature,
            distance=distance,
            similarity=max(0.0, round(similarity, 4)),
            verdict=verdict,
            changed_fields=changed,
        )

    @property
    def attractors(self) -> int:
        """Number of distinct states encountered by the oracle."""
        return len(self._seen)

    def compare_journals(self, old_path: str | Path, new_path: str | Path) -> dict[str, Any]:
        """Compare the latest valid records from two JSONL journals."""
        old_pulses = ResonanceLoom.load(old_path)
        new_pulses = ResonanceLoom.load(new_path)
        if not old_pulses or not new_pulses:
            raise ValueError("both resonance journals must contain at least one pulse")
        old = old_pulses[-1]
        new = new_pulses[-1]
        distance = self._distance(old["signature"], new["signature"])
        changed_fields = sorted(
            field for field in ("chaos", "mood", "mesh_events", "reactor_events", "state_keys")
            if old.get(field) != new.get(field)
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
