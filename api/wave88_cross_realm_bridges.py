"""Wave 88 — Cross-realm Coherence Bridges.

Establishes directed coherence pathways between the three previously
independent wave subsystems (gradient field, adaptive regulation,
memory graph). These bridges allow organized communication between
subsystems that previously operated in isolation.

The bridges form a "coherence lattice" — a structured network where
each subsystem can influence and be influenced by the others in
predictable, controllable ways.

This is the organism's "social nervous system" — enabling subsystems
to not just coexist, but to actively communicate and coordinate.
"""
from __future__ import annotations
import json, time, math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave88_cross_realm_bridges.json"


class CoherenceBridge:
    """A directed coherence bridge between two subsystems."""

    def __init__(self, source: str, target: str, bridge_id: str | None = None):
        self.source = source
        self.target = target
        self.bridge_id = bridge_id or f"{source}_to_{target}"
        self.strength = 0.5
        self.active = True
        self.message_history: List[dict] = []

    def transmit(self, message: dict, strength: float | None = None) -> dict:
        """Send a coherence message from source to target."""
        if not self.active:
            return {"status": "bridge_inactive", "bridge_id": self.bridge_id}

        if strength is not None:
            self.strength = max(0.0, min(1.0, strength))

        self.last_transmission = time.time()
        self.message_history.append({
            "timestamp": self.last_transmission,
            "message": message,
            "strength": self.strength,
        })

        if len(self.message_history) > 100:
            self.message_history = self.message_history[-50:]

        return {
            "status": "transmitted",
            "bridge_id": self.bridge_id,
            "source": self.source,
            "target": self.target,
            "message": message,
            "strength": round(self.strength, 3),
            "timestamp": self.last_transmission,
        }

    def receive(self, message: dict, strength: float | None = None) -> dict:
        """Receive a coherence message at the target end."""
        if strength is not None:
            self.strength = max(0.0, min(1.0, strength))
        self.message_history.append({
            "timestamp": time.time(),
            "message": message,
            "strength": self.strength,
        })
        return {
            "status": "received",
            "bridge_id": self.bridge_id,
            "source": self.source,
            "target": self.target,
            "strength": round(self.strength, 3),
        }


class CrossRealmCoherenceLattice:
    """The organism's cross-realm coherence bridge network."""

    def __init__(self):
        self.subsystems = ["gradient", "regulation", "memory"]
        self.bridges: Dict[str, CoherenceBridge] = {}

        for source in self.subsystems:
            for target in self.subsystems:
                if source != target:
                    bridge_id = f"{source}_to_{target}"
                    self.bridges[bridge_id] = CoherenceBridge(source, target, bridge_id)

        self.integration_history: List[dict] = []
        self.cycle = 0
        self.lattice_stability = 1.0

    def reset(self) -> None:
        """Reset the lattice to its initial state."""
        self.integration_history = []
        self.cycle = 0
        self.lattice_stability = 1.0
        for bridge in self.bridges.values():
            bridge.strength = 0.5
            bridge.active = True

    def connect(self, source: str, target: str, strength: float = 0.5) -> dict:
        """Activate or strengthen a coherence bridge."""
        bridge_id = f"{source}_to_{target}"
        if bridge_id in self.bridges:
            self.bridges[bridge_id].strength = max(0.0, min(1.0, strength))
            self.bridges[bridge_id].active = True
            return {"status": "bridge_activated", "bridge_id": bridge_id,
                    "strength": self.bridges[bridge_id].strength}
        return {"status": "unknown_bridge", "requested": bridge_id}

    def broadcast(self, source: str, message: dict) -> Dict[str, dict]:
        """Broadcast a message from one subsystem to all others."""
        results = {}
        for target in self.subsystems:
            if source != target:
                bridge_id = f"{source}_to_{target}"
                results[target] = self.bridges[bridge_id].transmit(message)
        return results

    def integrate_cycle(self) -> dict:
        """One full integration cycle across all bridges."""
        self.cycle += 1
        stability_factors = []

        for bridge in self.bridges.values():
            bridge.strength = max(0.0, bridge.strength - 0.0001 * self.cycle)
            stability_factors.append(bridge.strength)

        if stability_factors:
            self.lattice_stability = sum(stability_factors) / len(stability_factors)
        else:
            self.lattice_stability = 1.0

        entry = {
            "cycle": self.cycle,
            "lattice_stability": round(self.lattice_stability, 4),
            "active_bridges": sum(1 for b in self.bridges.values() if b.active),
            "avg_bridge_strength": round(self.lattice_stability, 4),
        }
        self.integration_history.append(entry)

        if len(self.integration_history) > 200:
            self.integration_history = self.integration_history[-100:]
        return entry

    def get_lattice_status(self) -> dict:
        """Return current lattice state."""
        active_count = sum(1 for b in self.bridges.values() if b.active)
        avg_strength = sum(b.strength for b in self.bridges.values()) / len(self.bridges) if self.bridges else 0
        return {
            "lattice_stability": round(self.lattice_stability, 4),
            "active_bridges": active_count,
            "total_bridges": len(self.bridges),
            "avg_bridge_strength": round(avg_strength, 4),
            "subsystems": self.subsystems,
            "cycle": self.cycle,
        }


def coherence_vitals() -> dict:
    return {"organ": "wave88_cross_realm_bridges", "wave": 88, "status": "active"}


def _load() -> dict:
    if STATE_FILE.exists():
        try:
            data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            return data
        except Exception:
            pass
    return {"history": [], "cycle": 0, "lattice_stability": 1.0}


def _save(state: dict) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def handler(req: dict = None) -> dict:
    req = req or {}
    action = req.get("action", "status")
    state = _load()
    lattice = CrossRealmCoherenceLattice()

    if "cycle" in state:
        lattice.cycle = state["cycle"]
    if "lattice_stability" in state:
        lattice.lattice_stability = state["lattice_stability"]

    if action == "status":
        status = lattice.get_lattice_status()
        return {"action": "status", "wave": 88, **status}

    elif action == "connect":
        source = req.get("source", "")
        target = req.get("target", "")
        strength = req.get("strength", 0.5)
        result = lattice.connect(source, target, strength)
        return {"action": "connect", **result}

    elif action == "broadcast":
        source = req.get("source", "")
        message = req.get("message", {})
        results = lattice.broadcast(source, message)
        return {"action": "broadcast", "results": results}

    elif action == "integrate":
        result = lattice.integrate_cycle()
        state["cycle"] = lattice.cycle
        state["lattice_stability"] = lattice.lattice_stability
        _save(state)
        return {"action": "integrate", **result}

    elif action == "lattice_status":
        status = lattice.get_lattice_status()
        return {"action": "lattice_status", "wave": 88, **status}

    elif action == "reset":
        lattice.reset()
        state = {"history": [], "cycle": 0, "lattice_stability": 1.0}
        _save(state)
        return {"action": "reset", "reset": True, "message": "Lattice reset"}

    else:
        return {"error": f"unknown action: {action}"}


if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    result = handler({"action": action})
    print(json.dumps(result, indent=2, default=str))
