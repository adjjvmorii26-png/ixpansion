"""Foundation coordinator for the IXPANSION agent, lattice, trust, and federation layers."""

from __future__ import annotations

import os
import uuid
from typing import Any, Optional

from agent import Agent
from federated_stack import run_1_3_stack
from lattice_stack import MachineLattice
from security_controls import AuditStore, TrustStore


class AetherLattice:
    """Compose the offline project layers into one inspectable runtime."""

    def __init__(
        self,
        agent: Optional[Agent] = None,
        lattice: Optional[MachineLattice] = None,
        trust: Optional[TrustStore] = None,
        audits: Optional[AuditStore] = None,
    ):
        self.agent = agent or Agent(name="aether-agent")
        self.lattice = lattice or MachineLattice()
        self.trust = trust or TrustStore()
        self.audits = audits or AuditStore(":memory:")

    def snapshot(self) -> dict[str, Any]:
        federation = run_1_3_stack(
            green_scores={
                machine_id: machine.health
                for machine_id, machine in self.lattice.machines.items()
            }
            or None
        )
        return {
            "name": "aether-lattice",
            "version": "0.1",
            "agent": {
                "name": self.agent.name,
                "memory_entries": len(self.agent.memory),
                "history_entries": len(self.agent.history),
                "skills": len(self.agent.skills),
            },
            "lattice": self.lattice.snapshot(),
            "federation": {
                "primary_carbon_federate": federation["primary_carbon_federate"],
                "winner_cluster": federation["si"]["winner_cluster"],
                "best_fitness": federation["si"]["best_fitness"],
                "transport": federation["transport"],
            },
            "trust": {
                "known_subjects": len(self.trust.values),
                "foundation": self.trust.trust("agent:aether"),
            },
            "safety": {
                "audit_records": len(self.audits.decisions()),
                "protected_gate_actions": ["PROD_DEPLOY", "SECRET_ROTATE"],
            },
            "swarm": {
                "role": os.getenv("SWARM_ROLE", "foundation"),
                "token_required": bool(os.getenv("SWARM_TOKEN")),
            },
        }

    def dispatch(
        self,
        task: str,
        *,
        critical: bool = False,
        lease_seconds: Optional[float] = None,
        operator: str = "aether",
        task_id: Optional[str] = None,
    ) -> dict[str, Any]:
        if not task.strip():
            raise ValueError("task is required")
        correlation_id = task_id or uuid.uuid4().hex
        if lease_seconds is None:
            machine_id = self.lattice.allocate(task, critical=critical)
            lease = None
        else:
            lease = self.lattice.acquire(
                task,
                duration=lease_seconds,
                critical=critical,
            )
            machine_id = lease.machine_id
        node_trust = self.trust.observe(f"node:{machine_id}", True)
        self.audits.record(
            correlation_id,
            {"AETHER_DISPATCH"},
            node_trust,
            operator,
            "ALLOCATED",
            correlation_id=correlation_id,
        )
        result = self.agent.run(task)
        return {
            "task_id": correlation_id,
            "task": task,
            "machine_id": machine_id,
            "critical": critical,
            "lease": None
            if lease is None
            else {"expires_at": lease.expires_at},
            "agent": result,
            "node_trust": node_trust,
        }
