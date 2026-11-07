"""Mandatory scoped-grant bridge into the provider-neutral Plugin Runtime.

Hosts must expose this bridge, not raw adapter/runtime execution, to callers.
"""
from dataclasses import replace
from datetime import datetime, timezone

from ixpansion_workbench.runtime import ApprovalClass, ExecutionContext, PluginRuntime

from .authorization import AuthorizationGrant, grant_payload
from .grant import GrantAuthority


_RISK_CLASS = {
    "R0": ApprovalClass.READ,
    "R1": ApprovalClass.REVERSIBLE_WRITE,
    "R2": ApprovalClass.SENSITIVE_WRITE,
    "R3": ApprovalClass.PRODUCTION,
    "R4": ApprovalClass.DESTRUCTIVE,
}


class GrantRejected(PermissionError):
    pass


def execute_authorized(*, runtime: PluginRuntime, adapter_id: str,
                       capability_name: str, payload: dict,
                       context: ExecutionContext, grant: AuthorizationGrant,
                       grant_authority: GrantAuthority, verified_tenant_id: str,
                       operation: str, now: datetime | None = None):
    """Validate a short-lived, resource-bound Identity Gate grant before dispatch."""
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None or grant.issued_at.tzinfo is None or grant.expires_at.tzinfo is None:
        raise GrantRejected("Timezone-aware grant timestamps are required.")
    if not (grant.issued_at <= now < grant.expires_at):
        raise GrantRejected("Authorization grant is expired or not yet valid.")
    try:
        signature_valid = grant_authority.verify(grant_payload(grant), grant.signature)
    except Exception:
        signature_valid = False
    if not signature_valid:
        raise GrantRejected("Authorization grant signature is invalid.")
    if grant.tenant_id != verified_tenant_id:
        raise GrantRejected("Grant tenant does not match verified host tenant.")
    if grant.actor_subject != context.actor:
        raise GrantRejected("Grant actor does not match execution context.")
    if grant.resource_id != context.target:
        raise GrantRejected("Grant resource does not match execution target.")
    if grant.operation != operation:
        raise GrantRejected("Grant operation does not match requested operation.")
    if grant.request_id != context.request_id:
        raise GrantRejected("Grant request ID does not match execution context.")
    approval_class = _RISK_CLASS.get(grant.risk)
    if approval_class is None:
        raise GrantRejected("Unknown risk class.")
    scoped_context = replace(context, approved_for=frozenset({approval_class}))
    return runtime.execute(adapter_id, capability_name, payload, scoped_context)
