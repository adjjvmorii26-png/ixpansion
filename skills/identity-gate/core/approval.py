"""Approval authority is independent from ordinary role permissions."""
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class ApprovalDecision:
    approved: bool
    approver_subject: str | None
    approved_at: datetime | None
    resource_id: str
    operation: str
    risk: str
    strong: bool = False
    recovery_plan_ref: str | None = None
    approval_ref: str | None = None


class ApprovalResolver(Protocol):
    def resolve(self, *, actor_subject: str, resource_id: str, operation: str,
                risk: str, strong_required: bool) -> ApprovalDecision | None:
        """Return a separately verified approval, or None when absent."""
        ...
