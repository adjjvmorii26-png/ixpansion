"""HypergraphOmniEngine — OMEGA-01 resonance core.

Deterministic multi-node hypergraph with bounded weights, entropy drift,
chained SHA-256 seals, and explicit recovery audit events.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import random
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class HypergraphEngineError(Exception):
    """Raised for invalid inputs or unrecoverable engine state."""


@dataclass
class HyperNode:
    name: str
    vector_weight: float = 0.5
    entropy_drift: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "vector_weight": self.vector_weight,
            "entropy_drift": self.entropy_drift,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HyperNode":
        return cls(
            name=data["name"],
            vector_weight=float(data["vector_weight"]),
            entropy_drift=float(data["entropy_drift"]),
        )


@dataclass
class AuditEvent:
    kind: str
    seal: str
    aggregate_drift: float
    detail: Dict[str, Any] = field(default_factory=dict)


class HypergraphOmniEngine:
    """Seeded hypergraph resonance engine with full-digest seals and rollback."""

    MAX_HISTORY = 64
    MAX_CYCLES = 50
    DEFAULT_NODES = (
        "node_genome",
        "node_atlas",
        "node_lattice",
        "node_oracle",
        "node_veil",
    )

    def __init__(self, seed: int = 42) -> None:
        self.seed = int(seed)
        self._rng = random.Random(self.seed)
        self.nodes: Dict[str, HyperNode] = {
            name: HyperNode(name=name, vector_weight=0.5 + 0.01 * i)
            for i, name in enumerate(self.DEFAULT_NODES)
        }
        self.edges: Dict[str, set] = {n: set() for n in self.nodes}
        self.resonance_manifold_history: List[Dict[str, Any]] = []
        self.audit_chain: List[AuditEvent] = []
        self._audit_head: str = "0xOMEGA_GENESIS"
        self.last_known_good_state: Optional[Dict[str, Any]] = None
        self._lock = asyncio.Lock()
        self._snapshot_weights()

    # ------------------------------------------------------------------ utils
    def _snapshot_weights(self) -> None:
        """Capture full recoverable state (weights, drifts, RNG, audit head)."""
        self.last_known_good_state = {
            "nodes": {k: v.to_dict() for k, v in self.nodes.items()},
            "edges": {k: list(v) for k, v in self.edges.items()},
            "rng_state": self._rng.getstate(),
            "audit_head": self._audit_head,
            "history_len": len(self.resonance_manifold_history),
        }

    def _restore_from_snapshot(self) -> None:
        if self.last_known_good_state is None:
            raise HypergraphEngineError("no last_known_good_state to restore")
        snap = self.last_known_good_state
        self.nodes = {k: HyperNode.from_dict(v) for k, v in snap["nodes"].items()}
        self.edges = {k: set(v) for k, v in snap["edges"].items()}
        self._rng.setstate(snap["rng_state"])
        self._audit_head = snap["audit_head"]
        # Trim history to pre-pulse length
        target = snap["history_len"]
        self.resonance_manifold_history = self.resonance_manifold_history[:target]

    def _validate_cycles(self, cycles: Any) -> int:
        if isinstance(cycles, bool) or not isinstance(cycles, int):
            raise HypergraphEngineError(
                f"cycles must be a non-boolean int in [1, {self.MAX_CYCLES}], got {cycles!r}"
            )
        if cycles < 1 or cycles > self.MAX_CYCLES:
            raise HypergraphEngineError(
                f"cycles must be in [1, {self.MAX_CYCLES}], got {cycles}"
            )
        return cycles

    def _generate_canonical_seal(self, aggregate_drift: float) -> str:
        """Full SHA-256 digest (64 hex chars) — no truncation."""
        payload = {
            "nodes": {k: v.to_dict() for k, v in sorted(self.nodes.items())},
            "aggregate_drift": round(float(aggregate_drift), 12),
            "prev": self._audit_head,
            "seed": self.seed,
        }
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest().upper()
        seal = f"0xOMEGA_{digest}"
        return seal

    def _emit_audit(self, kind: str, seal: str, aggregate_drift: float, **detail: Any) -> None:
        evt = AuditEvent(
            kind=kind,
            seal=seal,
            aggregate_drift=aggregate_drift,
            detail=detail,
        )
        self.audit_chain.append(evt)
        self._audit_head = seal

    # ----------------------------------------------------------------- public
    def entangle_nodes(self, a: str, b: str) -> None:
        if a not in self.nodes or b not in self.nodes:
            raise HypergraphEngineError(f"unknown node reference: {a!r} / {b!r}")
        if a == b:
            raise HypergraphEngineError("cannot entangle a node with itself")
        self.edges[a].add(b)
        self.edges[b].add(a)

    async def execute_resonance_cycle(self, cycles: int = 1) -> List[Dict[str, Any]]:
        cycles = self._validate_cycles(cycles)
        results: List[Dict[str, Any]] = []

        async with self._lock:
            self._snapshot_weights()
            try:
                for _ in range(cycles):
                    # Deterministic pulse
                    aggregate = 0.0
                    for node in self.nodes.values():
                        delta = self._rng.uniform(-0.02, 0.02)
                        node.vector_weight = max(
                            0.0, min(1.0, node.vector_weight + delta)
                        )
                        drift = abs(delta) * 0.1
                        node.entropy_drift = min(0.05, node.entropy_drift + drift)
                        aggregate += node.entropy_drift

                    aggregate_drift = aggregate / max(1, len(self.nodes))
                    # Anomaly recovery path (explicit pre/post audit)
                    recovered = False
                    if aggregate_drift > 0.04:
                        pre_seal = self._generate_canonical_seal(aggregate_drift)
                        self._emit_audit(
                            "pre_recovery",
                            pre_seal,
                            aggregate_drift,
                            reason="aggregate_drift_threshold",
                        )
                        # Soft recovery: clamp drifts
                        for node in self.nodes.values():
                            node.entropy_drift = min(0.03, node.entropy_drift * 0.5)
                        aggregate_drift = sum(
                            n.entropy_drift for n in self.nodes.values()
                        ) / max(1, len(self.nodes))
                        recovered = True

                    seal = self._generate_canonical_seal(aggregate_drift)
                    if recovered:
                        self._emit_audit(
                            "post_recovery",
                            seal,
                            aggregate_drift,
                            recovered=True,
                        )
                    else:
                        self._emit_audit("pulse", seal, aggregate_drift)

                    record = {
                        "aggregate_drift": aggregate_drift,
                        "chained_seal": seal,
                        "recovered": recovered,
                    }
                    self.resonance_manifold_history.append(record)
                    if len(self.resonance_manifold_history) > self.MAX_HISTORY:
                        self.resonance_manifold_history = (
                            self.resonance_manifold_history[-self.MAX_HISTORY :]
                        )
                    results.append(record)

                # Successful cycle batch → update known-good
                self._snapshot_weights()
            except Exception:
                self._restore_from_snapshot()
                raise

        return results
