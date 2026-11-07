"""Secret-safe audit event model and sink contract."""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Protocol
import hashlib
import json
import re


_SECRET = re.compile(r"(token|secret|password|api[_-]?key|authorization|cookie|private[_-]?key)", re.I)


def redact(value: Any, key: str = "") -> Any:
    if _SECRET.search(key):
        return "[REDACTED]"
    if isinstance(value, Mapping):
        return {str(k): redact(v, str(k)) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [redact(v) for v in value]
    if isinstance(value, str):
        return re.sub(r"(?i)(Bearer\\s+)[A-Za-z0-9._~+/=-]+", r"\\1[REDACTED]", value)
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return str(value)


@dataclass(frozen=True)
class AuditEvent:
    actor_identity: str
    authentication_source: str
    resource_owner: str | None
    resource_id: str
    requested_operation: str
    permission_evaluated: str
    approval_identity: str | None
    approval_timestamp: datetime | None
    execution_result: str
    before_ref: str | None = None
    after_ref: str | None = None
    event_id: str = ""
    occurred_at: datetime | None = None
    metadata: Mapping[str, Any] | None = None

    def normalized(self) -> dict[str, Any]:
        data = redact({
            "actor_identity": self.actor_identity,
            "authentication_source": self.authentication_source,
            "resource_owner": self.resource_owner,
            "resource_id": self.resource_id,
            "requested_operation": self.requested_operation,
            "permission_evaluated": self.permission_evaluated,
            "approval_identity": self.approval_identity,
            "approval_timestamp": self.approval_timestamp.isoformat() if self.approval_timestamp else None,
            "execution_result": self.execution_result,
            "before_ref": self.before_ref,
            "after_ref": self.after_ref,
            "occurred_at": (self.occurred_at or datetime.now(timezone.utc)).isoformat(),
            "metadata": dict(self.metadata or {}),
        })
        data["event_id"] = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
        return data


class AuditSink(Protocol):
    def append(self, event: Mapping[str, Any]) -> str:
        """Durably append an event and return its audit event identifier."""
        ...
