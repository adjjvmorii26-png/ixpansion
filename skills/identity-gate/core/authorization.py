"""Fail-closed authorization pipeline for IXPANSION Workbench operations."""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Mapping

from .approval import ApprovalAuthorityResolver, ApprovalResolver
from .audit import AuditEvent, AuditSink
from .identity import IdentityVerifier, identity_is_current
from .ownership import OwnershipResolver, OwnershipStatus


class Decision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    HOLD = "HOLD"
    REVERIFY = "REVERIFY"
    ESCALATE = "ESCALATE"
    BLOCK = "BLOCK"


@dataclass(frozen=True)
class OperationPolicy:
    permission: str
    risk: str


DEFAULT_POLICIES: Mapping[str, OperationPolicy] = {
    "inspect": OperationPolicy("resource.read", "R0"),
    "analyze": OperationPolicy("resource.read", "R0"),
    "create_branch": OperationPolicy("change.propose", "R1"),
    "create_draft": OperationPolicy("change.propose", "R1"),
    "modify_file": OperationPolicy("resource.modify", "R2"),
    "update_database": OperationPolicy("resource.modify", "R2"),
    "merge": OperationPolicy("resource.modify", "R3"),
    "deploy": OperationPolicy("resource.modify", "R3"),
    "change_access": OperationPolicy("resource.manage", "R3"),
    "delete": OperationPolicy("resource.manage", "R4"),
    "rotate_credentials": OperationPolicy("resource.manage", "R4"),
    "destructive_migration": OperationPolicy("resource.manage", "R4"),
}


@dataclass(frozen=True)
class AuthorizationRequest:
    credential_ref: str
    resource_id: str
    operation: str
    request_id: str
    before_ref: str | None = None


@dataclass(frozen=True)
class AuthorizationResult:
    decision: Decision
    reason: str
    actor_subject: str | None = None
    permission: str | None = None
    risk: str | None = None
    grant: "AuthorizationGrant | None" = None
    audit_event_id: str | None = None


@dataclass(frozen=True)
class AuthorizationGrant:
    actor_subject: str
    tenant_id: str
    resource_id: str
    operation: str
    risk: str
    issued_at: datetime
    expires_at: datetime
    request_id: str


class IdentityGate:
    def __init__(self, *, verifier: IdentityVerifier, ownership: OwnershipResolver,
                 approvals: ApprovalResolver, approval_authority: ApprovalAuthorityResolver,
                 audit: AuditSink,
                 policies: Mapping[str, OperationPolicy] = DEFAULT_POLICIES,
                 grant_ttl: timedelta = timedelta(minutes=2)):
        if grant_ttl <= timedelta(0) or grant_ttl > timedelta(minutes=5):
            raise ValueError("grant_ttl must be positive and no more than five minutes")
        self.verifier, self.ownership = verifier, ownership
        self.approvals, self.approval_authority, self.audit = approvals, approval_authority, audit
        self.policies, self.grant_ttl = policies, grant_ttl

    def authorize(self, request: AuthorizationRequest,
                  now: datetime | None = None) -> AuthorizationResult:
        now = now or datetime.now(timezone.utc)
        policy = self.policies.get(request.operation)
        if policy is None:
            return self._finish(Decision.DENY, "Unknown operation.", None, request, None, None, None, now)
        try:
            identity = self.verifier.verify(request.credential_ref)
        except Exception:
            return self._finish(Decision.DENY, "Identity could not be verified.", None, request, policy, None, None, now)
        if not identity_is_current(identity, now):
            return self._finish(Decision.REVERIFY, "Identity is expired or invalid.", identity, request, policy, None, None, now)

        allowed = any("*" in _role_permissions(role) or policy.permission in _role_permissions(role)
                      for role in identity.roles)
        if not allowed:
            return self._finish(Decision.DENY, "Required permission is missing.", identity, request, policy, None, None, now)

        try:
            ownership = self.ownership.resolve(request.resource_id, identity.subject,
                                               identity.tenant_id, request.operation)
        except Exception:
            return self._finish(Decision.DENY, "Ownership could not be verified.", identity, request, policy, None, None, now)
        if ownership.resource_id != request.resource_id:
            return self._finish(Decision.DENY, "Ownership evidence is for a different resource.", identity, request, policy, ownership.owner_subject, None, now)
        if ownership.status == OwnershipStatus.CONFLICT:
            return self._finish(Decision.ESCALATE, "Conflicting resource ownership.", identity, request, policy, ownership.owner_subject, None, now)
        if ownership.tenant_id != identity.tenant_id:
            return self._finish(Decision.DENY, "Resource tenant does not match authenticated tenant.", identity, request, policy, ownership.owner_subject, None, now)
        owned = ownership.status == OwnershipStatus.VERIFIED and ownership.owner_subject == identity.subject
        delegated = (ownership.status == OwnershipStatus.DELEGATED
                     and ownership.delegate_subject == identity.subject
                     and request.operation in ownership.allowed_operations)
        if not (owned or delegated):
            return self._finish(Decision.DENY, "Ownership or scoped delegation is unverified.", identity, request, policy, ownership.owner_subject, None, now)

        approval = None
        if policy.risk in ("R3", "R4"):
            try:
                approval = self.approvals.resolve(
                    actor_subject=identity.subject, resource_id=request.resource_id,
                    operation=request.operation, risk=policy.risk,
                    strong_required=policy.risk == "R4",
                )
            except Exception:
                approval = None
            valid = (approval is not None and approval.approved
                     and approval.approver_subject is not None
                     and approval.approver_subject != identity.subject
                     and approval.resource_id == request.resource_id
                     and approval.operation == request.operation
                     and approval.risk == policy.risk
                     and approval.approved_at is not None
                     and approval.approved_at.tzinfo is not None
                     and approval.approved_at <= now
                     and approval.expires_at is not None
                     and approval.expires_at.tzinfo is not None
                     and now < approval.expires_at)
            if not valid:
                return self._finish(Decision.HOLD, "Explicit approval is missing, expired, or invalid.", identity, request, policy, ownership.owner_subject, approval, now)
            if policy.risk == "R4" and (not approval.strong or not approval.recovery_plan_ref):
                return self._finish(Decision.HOLD, "R4 requires strong approval and a recovery plan.", identity, request, policy, ownership.owner_subject, approval, now)
            try:
                authority_ok = self.approval_authority.is_authorized(
                    approver_subject=approval.approver_subject,
                    resource_id=request.resource_id, operation=request.operation,
                    risk=policy.risk,
                )
            except Exception:
                authority_ok = False
            if not authority_ok:
                return self._finish(Decision.HOLD, "Approver authority is not independently established.", identity, request, policy, ownership.owner_subject, approval, now)

        grant = AuthorizationGrant(identity.subject, identity.tenant_id, request.resource_id,
                                   request.operation, policy.risk, now, now + self.grant_ttl,
                                   request.request_id)
        return self._finish(Decision.ALLOW, "All identity, permission, ownership, and approval checks passed.",
                            identity, request, policy, ownership.owner_subject, approval, now, grant)

    def _finish(self, decision, reason, identity, request, policy, owner, approval, now, grant=None):
        risk = policy.risk if policy else None
        event = AuditEvent(
            actor_identity=identity.subject if identity else "unknown",
            authentication_source=identity.authentication_source if identity else "unknown",
            resource_owner=owner, resource_id=request.resource_id,
            requested_operation=request.operation,
            permission_evaluated=policy.permission if policy else "unknown",
            approval_identity=approval.approver_subject if approval else None,
            approval_timestamp=approval.approved_at if approval else None,
            execution_result=decision.value,
            before_ref=request.before_ref,
            metadata={"request_id": request.request_id, "risk": risk, "reason": reason},
            occurred_at=now,
        )
        try:
            audit_id = self.audit.append(event.normalized())
        except Exception:
            if risk in ("R2", "R3", "R4") or decision == Decision.ALLOW:
                return AuthorizationResult(Decision.BLOCK, "Audit persistence failed; operation blocked.",
                                           identity.subject if identity else None,
                                           policy.permission if policy else None, risk)
            audit_id = None
        return AuthorizationResult(decision, reason, identity.subject if identity else None,
                                   policy.permission if policy else None, risk, grant, audit_id)


def _role_permissions(role: str) -> frozenset[str]:
    return {
        "owner": frozenset({"*"}),
        "administrator": frozenset({"resource.manage", "resource.read", "change.propose"}),
        "maintainer": frozenset({"resource.read", "change.propose", "resource.modify"}),
        "contributor": frozenset({"resource.read", "change.propose"}),
        "auditor": frozenset({"resource.read", "evidence.read"}),
        "agent": frozenset({"resource.read", "change.propose", "delegated.execute"}),
    }.get(role, frozenset())
