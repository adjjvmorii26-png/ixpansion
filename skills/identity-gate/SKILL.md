---
name: identity-gate
description: Enforce verified identity, scoped permissions, resource ownership, approval authority, expiry, and evidence logging before IXPANSION Workbench operations.
---

# Identity Gate

## Capabilities
- identity-gate:verify — verify an actor through a trusted host identity verifier.
- identity-gate:authorize — evaluate role permissions, resource ownership/delegation, risk, approval, and expiry.
- identity-gate:audit — emit secret-redacted decision evidence and block sensitive writes if audit fails.

## Roots

| Area | Path |
|---|---|
| Core | `skills/identity-gate/core/` |
| Policies | `skills/identity-gate/policies/` |
| Tests | `skills/identity-gate/tests/` |

## Security contract

Authentication is not authorization. Access is not ownership. Ownership is not approval authority.

- Unknown or unverifiable identities are denied.
- Roles come only from the trusted identity provider, never from request payloads.
- Resource ownership or explicit, scoped delegation must be independently resolved.
- Approval is a separate decision from role permission and must be attributable to an authorized approver.
- Authorization grants are short-lived and bound to actor, resource, operation, and risk.
- R3 requires explicit approval. R4 requires strong approval and a recovery plan.
- Audit failure blocks R2-R4 operations.
- Never log credentials, tokens, secrets, or raw authentication material.
- This package defines host-injected interfaces. It does not authenticate users, prove provider ownership, or establish production identity by itself.

## Commands

### identity-gate:verify
The host supplies an IdentityVerifier implementation and opaque credential reference. Never pass credential values into the gate.

### identity-gate:authorize
The host supplies an AuthorizationRequest. The gate independently verifies identity, permission, ownership/delegation, approval, expiry, and auditability before issuing a grant.

### identity-gate:audit
Persist the resulting decision through a host-provided append-only audit sink. A failed sink is a hard failure for sensitive writes.
