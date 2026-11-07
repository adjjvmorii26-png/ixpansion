"""Approval evidence and independently verified approval authority."""
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
    expires_at: datetime | None = None
    strong: bool = False
    recovery_plan_ref: str | None = None
    approval_ref: str | None = None


class ApprovalResolver(Protocol):
    def resolve(self, *, actor_subject: str, resource_id: str, operation: str,
                risk: str, strong_required: bool) -> ApprovalDecision | None:
        """Return separately verified approval evidence, or None when absent."""
        ...


class ApprovalAuthorityResolver(Protocol):
    def is_authorized(self, *, approver_subject: str, resource_id: str,
                      operation: str, risk: str) -> bool:
        """Verify the approver's authority from an independent trusted source."""
        ...
