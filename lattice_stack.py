"""Safe reuse lattice for degraded machine capacity.

The lattice never treats an unhealthy machine as generally available. It routes
degraded capacity only to noncritical work and keeps untrusted or unusable
machines quarantined for inspection.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
import time
from typing import Dict, Iterable, List, Optional


class MachineState(str, Enum):
    HEALTHY = "healthy"
    REUSABLE = "reusable"
    QUARANTINED = "quarantined"


@dataclass(frozen=True)
class MachineLease:
    task: str
    machine_id: str
    expires_at: float


@dataclass(frozen=True)
class Machine:
    machine_id: str
    health: float
    capacity: float
    trust: float = 1.0
    load: float = 0.0
    last_seen: Optional[float] = None


@dataclass(frozen=True)
class LatticePolicy:
    healthy_threshold: float = 0.8
    reusable_health_floor: float = 0.3
    minimum_capacity: float = 0.1
    minimum_trust: float = 0.5
    heartbeat_timeout: Optional[float] = None

    def __post_init__(self) -> None:
        if not 0 <= self.reusable_health_floor <= self.healthy_threshold <= 1:
            raise ValueError("health thresholds must satisfy 0 <= floor <= healthy <= 1")
        if not 0 <= self.minimum_capacity <= 1:
            raise ValueError("minimum_capacity must be between 0 and 1")
        if not 0 <= self.minimum_trust <= 1:
            raise ValueError("minimum_trust must be between 0 and 1")
        if self.heartbeat_timeout is not None and self.heartbeat_timeout < 0:
            raise ValueError("heartbeat_timeout must be non-negative")


class MachineLattice:
    """Classify machines and allocate safe work across the resulting lanes."""

    def __init__(
        self,
        machines: Iterable[Machine] = (),
        policy: Optional[LatticePolicy] = None,
    ):
        self.policy = policy or LatticePolicy()
        self.machines: Dict[str, Machine] = {}
        self.leases: Dict[str, MachineLease] = {}
        for machine in machines:
            self.register(machine)

    def register(self, machine: Machine) -> MachineState:
        self._validate_machine(machine)
        if machine.machine_id in self.machines:
            raise ValueError(f"machine_id already registered: {machine.machine_id}")
        self.machines[machine.machine_id] = machine
        return self.classify(machine)

    def classify(self, machine: Machine, now: Optional[float] = None) -> MachineState:
        reference_time = time.time() if now is None else now
        if (
            self.policy.heartbeat_timeout is not None
            and machine.last_seen is not None
            and reference_time - machine.last_seen > self.policy.heartbeat_timeout
        ):
            return MachineState.QUARANTINED
        if machine.trust < self.policy.minimum_trust:
            return MachineState.QUARANTINED
        if machine.capacity < self.policy.minimum_capacity:
            return MachineState.QUARANTINED
        if machine.health >= self.policy.healthy_threshold:
            return MachineState.HEALTHY
        if machine.health >= self.policy.reusable_health_floor:
            return MachineState.REUSABLE
        return MachineState.QUARANTINED

    def heartbeat(
        self,
        machine_id: str,
        *,
        health: Optional[float] = None,
        capacity: Optional[float] = None,
        trust: Optional[float] = None,
        load: Optional[float] = None,
        now: Optional[float] = None,
    ) -> MachineState:
        """Update telemetry for a registered machine and return its state."""
        current = self.machines.get(machine_id)
        if current is None:
            raise KeyError(f"Unknown machine: {machine_id}")
        updated = replace(
            current,
            health=current.health if health is None else health,
            capacity=current.capacity if capacity is None else capacity,
            trust=current.trust if trust is None else trust,
            load=current.load if load is None else load,
            last_seen=time.time() if now is None else now,
        )
        self._validate_machine(updated)
        self.machines[machine_id] = updated
        return self.classify(updated, now=updated.last_seen)

    def reusable(self, include_healthy: bool = True) -> List[Machine]:
        allowed = {MachineState.REUSABLE}
        if include_healthy:
            allowed.add(MachineState.HEALTHY)
        return [
            machine
            for machine in self.machines.values()
            if self.classify(machine) in allowed
        ]

    def allocate(
        self,
        task: str,
        critical: bool = False,
        now: Optional[float] = None,
    ) -> str:
        """Return the best eligible machine, rejecting unsafe reuse requests."""
        if not task.strip():
            raise ValueError("task is required")
        reference_time = time.time() if now is None else now
        self._expire_leases(reference_time)
        candidates = [
            machine for machine in self.reusable(include_healthy=True)
            if machine.machine_id not in self.leases
        ]
        if critical:
            candidates = [
                machine
                for machine in candidates
                if self.classify(machine) is MachineState.HEALTHY
            ]
        if not candidates:
            raise LookupError(f"No eligible machine for task: {task}")
        selected = max(
            candidates,
            key=lambda machine: (
                self.classify(machine) is MachineState.REUSABLE,
                machine.capacity * (1 - machine.load),
                machine.health,
                machine.machine_id,
            ),
        )
        return selected.machine_id

    def acquire(
        self,
        task: str,
        duration: float = 60.0,
        critical: bool = False,
        now: Optional[float] = None,
    ) -> MachineLease:
        """Reserve an eligible machine for a bounded task lease."""
        if duration <= 0:
            raise ValueError("lease duration must be positive")
        timestamp = time.time() if now is None else now
        machine_id = self.allocate(task, critical=critical, now=timestamp)
        lease = MachineLease(task, machine_id, timestamp + duration)
        self.leases[machine_id] = lease
        return lease

    def release(self, machine_id: str) -> bool:
        """Release a lease and report whether one was active."""
        return self.leases.pop(machine_id, None) is not None

    def _expire_leases(self, now: float) -> None:
        for machine_id, lease in list(self.leases.items()):
            if lease.expires_at <= now:
                del self.leases[machine_id]

    def snapshot(self) -> dict:
        counts = {state.value: 0 for state in MachineState}
        for machine in self.machines.values():
            counts[self.classify(machine).value] += 1
        return {
            "machines": len(self.machines),
            "leases": len(self.leases),
            "states": counts,
            "reusable_for_noncritical": [
                machine.machine_id for machine in self.reusable(include_healthy=False)
            ],
            "quarantined": [
                machine.machine_id
                for machine in self.machines.values()
                if self.classify(machine) is MachineState.QUARANTINED
            ],
        }

    @staticmethod
    def _validate_machine(machine: Machine) -> None:
        if not machine.machine_id:
            raise ValueError("machine_id is required")
        for name, value in (
            ("health", machine.health),
            ("capacity", machine.capacity),
            ("trust", machine.trust),
            ("load", machine.load),
        ):
            if not 0 <= value <= 1:
                raise ValueError(f"{name} must be between 0 and 1")


def build_lattice_stack(machines: Iterable[Machine]) -> dict:
    """Build a deterministic summary for the reusable machine pool."""
    lattice = MachineLattice(machines)
    eligible = lattice.reusable(include_healthy=True)
    return {
        "summary": lattice.snapshot(),
        "noncritical_machine": (
            lattice.allocate("reclaimable-work") if eligible else None
        ),
    }