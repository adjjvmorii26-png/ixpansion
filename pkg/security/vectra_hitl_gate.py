#!/usr/bin/env python3
"""
Vectra HITL (Human-In-The-Loop) Security Gate
- Trust threshold + sensitive-tag veto
- Human approve/reject with trust re-check on approve
- Durable JSONL audit log
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

AUDIT_PATH = Path(__file__).parent / "content_output" / "hitl_audits.jsonl"

SENSITIVE_TAGS = frozenset({
    "PROD_DEPLOY", "PROD_DELETE", "SECRET_ROTATE", "PAYMENT", "ROOT_ACCESS",
})
DUAL_CONTROL_TAGS = frozenset({"PROD_DEPLOY", "SECRET_ROTATE", "PROD_DELETE"})


class GateDecision(str, Enum):
    ALLOW = "ALLOW"
    VETO = "VETO"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DENIED = "DENIED"


@dataclass
class WorkforceTask:
    task_id: str
    task_type: str
    agent_id: str
    trust_score: float = 1.0
    tags: List[str] = field(default_factory=list)
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GateAudit:
    task_id: str
    decision: str
    reasons: List[str]
    operator: Optional[str] = None
    trust_score: Optional[float] = None
    tags: Optional[List[str]] = None
    ts: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id, "decision": self.decision,
            "reasons": self.reasons, "operator": self.operator,
            "trust_score": self.trust_score, "tags": self.tags, "ts": self.ts,
        }


class VectraHITLGate:
    def __init__(
        self,
        trust_threshold: float = 0.50,
        sensitive_tags: Optional[Set[str]] = None,
        audit_path: Optional[Path] = None,
        dual_control_tags: Optional[Set[str]] = None,
    ):
        self.trust_threshold = trust_threshold
        self.sensitive_tags = set(sensitive_tags or SENSITIVE_TAGS)
        self.dual_control_tags = set(dual_control_tags or DUAL_CONTROL_TAGS)
        self.audit_path = Path(audit_path or AUDIT_PATH)
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)
        self.paused: Dict[str, WorkforceTask] = {}
        self.approvals: Dict[str, List[str]] = {}
        self.audits: List[GateAudit] = []

    def _persist(self, audit: GateAudit) -> None:
        self.audits.append(audit)
        try:
            self.audit_path.parent.mkdir(parents=True, exist_ok=True)
            with self.audit_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(audit.to_dict()) + "\n")
        except OSError:
            pass

    def evaluate(self, task: WorkforceTask) -> GateAudit:
        reasons: List[str] = []
        if task.trust_score < self.trust_threshold:
            reasons.append(
                f"Assigned agent trust score ({task.trust_score:.2f}) < threshold ({self.trust_threshold:.2f})"
            )
        hit = [t for t in task.tags if t in self.sensitive_tags]
        if hit:
            reasons.append(f"Sensitive operation detected tags: {hit}")
        decision = GateDecision.VETO.value if reasons else GateDecision.ALLOW.value
        if reasons:
            self.paused[task.task_id] = task
        audit = GateAudit(
            task_id=task.task_id, decision=decision, reasons=reasons,
            trust_score=task.trust_score, tags=list(task.tags),
        )
        self._persist(audit)
        return audit

    def needs_dual_control(self, task: WorkforceTask) -> bool:
        return any(t in self.dual_control_tags for t in task.tags)

    def human_approve(self, task_id: str, operator: str, current_trust: Optional[float] = None) -> GateAudit:
        task = self.paused.get(task_id)
        if task is None:
            audit = GateAudit(task_id=task_id, decision=GateDecision.DENIED.value,
                              reasons=["not paused"], operator=operator)
            self._persist(audit)
            return audit
        trust = task.trust_score if current_trust is None else current_trust
        if trust < self.trust_threshold:
            audit = GateAudit(
                task_id=task_id, decision=GateDecision.DENIED.value,
                reasons=[f"trust re-check failed ({trust:.2f}) < {self.trust_threshold:.2f}"],
                operator=operator, trust_score=trust, tags=list(task.tags),
            )
            self._persist(audit)
            return audit
        ops = self.approvals.setdefault(task_id, [])
        if operator not in ops:
            ops.append(operator)
        if self.needs_dual_control(task) and len(ops) < 2:
            audit = GateAudit(
                task_id=task_id, decision=GateDecision.VETO.value,
                reasons=[f"dual-control pending ({len(ops)}/2): {ops}"],
                operator=operator, trust_score=trust, tags=list(task.tags),
            )
            self._persist(audit)
            return audit
        self.paused.pop(task_id, None)
        self.approvals.pop(task_id, None)
        audit = GateAudit(
            task_id=task_id, decision=GateDecision.APPROVED.value,
            reasons=["human approved"] + ([f"dual-control: {ops}"] if len(ops) >= 2 else []),
            operator=operator, trust_score=trust, tags=list(task.tags),
        )
        self._persist(audit)
        return audit

    def human_reject(self, task_id: str, operator: str) -> GateAudit:
        self.paused.pop(task_id, None)
        self.approvals.pop(task_id, None)
        audit = GateAudit(
            task_id=task_id, decision=GateDecision.REJECTED.value,
            reasons=["human rejected"], operator=operator,
        )
        self._persist(audit)
        return audit

    def snapshot(self) -> dict:
        return {
            "trust_threshold": self.trust_threshold,
            "paused": list(self.paused.keys()),
            "audits": len(self.audits),
            "vetoes": sum(1 for a in self.audits if a.decision == GateDecision.VETO.value),
            "audit_path": str(self.audit_path),
        }
