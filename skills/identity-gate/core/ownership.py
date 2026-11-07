"""Independent resource ownership and scoped delegation contracts."""
from dataclasses import dataclass
from typing import Protocol


class OwnershipStatus:
    VERIFIED = "verified"
    DELEGATED = "delegated"
    UNKNOWN = "unknown"
    CONFLICT = "conflict"


@dataclass(frozen=True)
class OwnershipDecision:
    status: str
    owner_subject: str | None
    resource_id: str
    delegate_subject: str | None = None
    allowed_operations: frozenset[str] = frozenset()
    tenant_id: str | None = None
    evidence_ref: str | None = None


class OwnershipResolver(Protocol):
    def resolve(self, resource_id: str, actor_subject: str, tenant_id: str,
                operation: str) -> OwnershipDecision:
        """Resolve ownership/delegation from an authoritative resource registry."""
        ...
