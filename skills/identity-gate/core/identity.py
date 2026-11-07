"""Trusted identity verification contracts. No provider credentials are stored here."""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol


class IdentityError(RuntimeError):
    pass


@dataclass(frozen=True)
class VerifiedIdentity:
    subject: str
    issuer: str
    authentication_source: str
    roles: frozenset[str]
    authenticated_at: datetime
    expires_at: datetime
    tenant_id: str


class IdentityVerifier(Protocol):
    def verify(self, credential_ref: str) -> VerifiedIdentity:
        """Resolve an opaque host-side credential reference to trusted claims."""
        ...


def identity_is_current(identity: VerifiedIdentity, now: datetime | None = None) -> bool:
    now = now or datetime.now(timezone.utc)
    if not isinstance(identity, VerifiedIdentity):
        return False
    if not identity.subject or not identity.issuer or not identity.tenant_id:
        return False
    if not isinstance(identity.authenticated_at, datetime) or not isinstance(identity.expires_at, datetime):
        return False
    if identity.authenticated_at.tzinfo is None or identity.expires_at.tzinfo is None:
        return False
    return identity.authenticated_at <= now < identity.expires_at
