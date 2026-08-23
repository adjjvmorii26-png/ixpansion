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
