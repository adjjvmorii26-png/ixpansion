import unittest
from datetime import datetime, timedelta, timezone

import importlib
_core = importlib.import_module("skills.identity-gate.core")
ApprovalDecision = _core.ApprovalDecision
AuthorizationRequest = _core.AuthorizationRequest
Decision = _core.Decision
IdentityGate = _core.IdentityGate
OwnershipDecision = _core.OwnershipDecision
OwnershipStatus = _core.OwnershipStatus
VerifiedIdentity = _core.VerifiedIdentity


NOW = datetime(2026, 11, 7, 12, tzinfo=timezone.utc)


class Verifier:
    def __init__(self, identity=None, error=False):
        self.identity, self.error = identity, error
    def verify(self, credential_ref):
        if self.error:
            raise RuntimeError("untrusted")
        return self.identity


class Ownership:
    def __init__(self, decision):
        self.decision = decision
    def resolve(self, *args):
        return self.decision


class Approvals:
    def __init__(self, decision=None):
        self.decision = decision
    def resolve(self, **kwargs):
        return self.decision


class ApprovalAuthority:
    def __init__(self, allowed=False):
        self.allowed = allowed
    def is_authorized(self, **kwargs):
        return self.allowed


class Audit:
    def __init__(self, fail=False):
        self.events, self.fail = [], fail
    def append(self, event):
        if self.fail:
            raise OSError("audit unavailable")
        self.events.append(event)
        return event["event_id"]


def identity(roles=("maintainer",), expiry=NOW + timedelta(minutes=10)):
    return VerifiedIdentity("actor-1", "test-issuer", "oidc:test",
                            frozenset(roles), NOW - timedelta(minutes=1),
                            expiry, "tenant-a")


def owned():
    return OwnershipDecision(OwnershipStatus.VERIFIED, "actor-1", "repo:one",
                             tenant_id="tenant-a")


def gate(*, ident=None, owner=None, approval=None, audit=None,
         verifier_error=False, approver_authorized=False):
    return IdentityGate(
        verifier=Verifier(ident or identity(), verifier_error),
        ownership=Ownership(owner or owned()),
        approvals=Approvals(approval),
        approval_authority=ApprovalAuthority(approver_authorized),
        audit=audit or Audit(),
    )


def valid_approval(risk="R3", strong=False, recovery=None):
    return ApprovalDecision(True, "owner-2", NOW - timedelta(seconds=5),
                            "repo:one", "deploy" if risk == "R3" else "delete",
                            risk, NOW + timedelta(minutes=1), strong, recovery, "approval:42")


class IdentityGateTests(unittest.TestCase):
    def test_unknown_identity_denied(self):
        self.assertEqual(gate(verifier_error=True).authorize(
            AuthorizationRequest("opaque", "repo:one", "inspect", "r1"), NOW
        ).decision, Decision.DENY)

    def test_expired_identity_requires_reverify(self):
        self.assertEqual(gate(ident=identity(expiry=NOW)).authorize(
            AuthorizationRequest("opaque", "repo:one", "inspect", "r1"), NOW
        ).decision, Decision.REVERIFY)

    def test_unknown_operation_denied(self):
        self.assertEqual(gate().authorize(
            AuthorizationRequest("opaque", "repo:one", "shell_exec", "r1"), NOW
        ).decision, Decision.DENY)

    def test_missing_permission_denied(self):
        self.assertEqual(gate(ident=identity(("auditor",))).authorize(
            AuthorizationRequest("opaque", "repo:one", "modify_file", "r1"), NOW
        ).decision, Decision.DENY)

    def test_unverified_owner_denied(self):
        foreign = OwnershipDecision(OwnershipStatus.VERIFIED, "someone-else",
                                    "repo:one", tenant_id="tenant-a")
        self.assertEqual(gate(owner=foreign).authorize(
            AuthorizationRequest("opaque", "repo:one", "inspect", "r1"), NOW
        ).decision, Decision.DENY)

    def test_cross_tenant_denied(self):
        foreign = OwnershipDecision(OwnershipStatus.VERIFIED, "actor-1",
                                    "repo:one", tenant_id="tenant-b")
        self.assertEqual(gate(owner=foreign).authorize(
            AuthorizationRequest("opaque", "repo:one", "inspect", "r1"), NOW
        ).decision, Decision.DENY)

    def test_ownership_evidence_for_other_resource_denied(self):
        foreign = OwnershipDecision(OwnershipStatus.VERIFIED, "actor-1",
                                    "repo:other", tenant_id="tenant-a")
        self.assertEqual(gate(owner=foreign).authorize(
            AuthorizationRequest("opaque", "repo:one", "inspect", "r1"), NOW
        ).decision, Decision.DENY)

    def test_conflicting_owner_escalates(self):
        conflict = OwnershipDecision(OwnershipStatus.CONFLICT, None,
                                     "repo:one", tenant_id="tenant-a")
        self.assertEqual(gate(owner=conflict).authorize(
            AuthorizationRequest("opaque", "repo:one", "inspect", "r1"), NOW
        ).decision, Decision.ESCALATE)

    def test_missing_r3_approval_holds(self):
        self.assertEqual(gate().authorize(
            AuthorizationRequest("opaque", "repo:one", "deploy", "r1"), NOW
        ).decision, Decision.HOLD)

    def test_approval_without_independent_authority_holds(self):
        result = gate(approval=valid_approval()).authorize(
            AuthorizationRequest("opaque", "repo:one", "deploy", "r1"), NOW
        )
        self.assertEqual(result.decision, Decision.HOLD)

    def test_expired_approval_holds(self):
        approval = ApprovalDecision(True, "owner-2", NOW - timedelta(minutes=5),
                                    "repo:one", "deploy", "R3",
                                    NOW - timedelta(seconds=1), approval_ref="approval:expired")
        self.assertEqual(gate(approval=approval, approver_authorized=True).authorize(
            AuthorizationRequest("opaque", "repo:one", "deploy", "r1"), NOW
        ).decision, Decision.HOLD)

    def test_valid_r3_requires_independent_approval_authority(self):
        result = gate(approval=valid_approval(), approver_authorized=True).authorize(
            AuthorizationRequest("opaque", "repo:one", "deploy", "r1"), NOW
        )
        self.assertEqual(result.decision, Decision.ALLOW)
        self.assertEqual(result.grant.risk, "R3")

    def test_r4_requires_strong_approval_and_recovery_plan(self):
        approval = valid_approval("R4", strong=False)
        self.assertEqual(gate(ident=identity(("owner",)), approval=approval,
                              approver_authorized=True).authorize(
            AuthorizationRequest("opaque", "repo:one", "delete", "r1"), NOW
        ).decision, Decision.HOLD)

    def test_audit_failure_blocks_sensitive_write(self):
        self.assertEqual(gate(audit=Audit(fail=True)).authorize(
            AuthorizationRequest("opaque", "repo:one", "modify_file", "r1"), NOW
        ).decision, Decision.BLOCK)

    def test_r0_audit_failure_does_not_grant(self):
        self.assertEqual(gate(audit=Audit(fail=True)).authorize(
            AuthorizationRequest("opaque", "repo:one", "inspect", "r1"), NOW
        ).decision, Decision.BLOCK)

    def test_successful_r0_grant_is_resource_bound_and_short_lived(self):
        result = gate().authorize(AuthorizationRequest(
            "opaque", "repo:one", "inspect", "request-42"
        ), NOW)
        self.assertEqual(result.decision, Decision.ALLOW)
        self.assertEqual(result.grant.resource_id, "repo:one")
        self.assertEqual(result.grant.expires_at - NOW, timedelta(minutes=2))
        self.assertEqual(result.grant.operation, "inspect")


if __name__ == "__main__":
    unittest.main()
