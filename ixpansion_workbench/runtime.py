"""Provider-neutral plugin execution with policy gates and evidence.

This module deliberately contains no provider SDKs and never reads credentials.
Concrete adapters are injected by the host application from authorized connectors.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import os
from pathlib import Path
import re
import threading
import time
from typing import Any, Callable, Mapping, Protocol


class Outcome(str, Enum):
    VERIFIED = "verified"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"
    NOT_RUN = "not_run"
    UNVERIFIED = "unverified"


class ApprovalClass(str, Enum):
    READ = "read"
    REVERSIBLE_WRITE = "reversible_write"
    SENSITIVE_WRITE = "sensitive_write"
    DESTRUCTIVE = "destructive"
    PRODUCTION = "production"


@dataclass(frozen=True)
class Capability:
    name: str
    approval: ApprovalClass = ApprovalClass.READ
    idempotent: bool = True
    verify_after_write: bool = True


@dataclass(frozen=True)
class ExecutionContext:
    actor: str
    target: str
    approved_for: frozenset[ApprovalClass] = frozenset()
    request_id: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutionResult:
    outcome: Outcome
    adapter: str
    capability: str
    target: str
    attempts: int = 0
    value: Any = None
    evidence_id: str | None = None
    message: str = ""


class Adapter(Protocol):
    adapter_id: str

    def capabilities(self) -> Mapping[str, Capability]: ...
    def execute(self, capability: str, payload: Mapping[str, Any],
                context: ExecutionContext) -> Any: ...
    def verify(self, capability: str, payload: Mapping[str, Any],
               result: Any, context: ExecutionContext) -> bool: ...


class PolicyError(RuntimeError):
    pass


_SECRET_KEY = re.compile(
    r"(token|secret|password|passwd|api[_-]?key|authorization|cookie|private[_-]?key)",
    re.IGNORECASE,
)


def _redact(value: Any, key: str = "") -> Any:
    if _SECRET_KEY.search(key):
        return "[REDACTED]"
    if isinstance(value, Mapping):
        return {str(k): _redact(v, str(k)) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_redact(v) for v in value]
    if isinstance(value, str):
        # Scrub common credential-bearing header/value patterns.
        return re.sub(
            r"(?i)(Bearer\s+)[A-Za-z0-9._~+/=-]+",
            r"\1[REDACTED]", value,
        )
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return str(value)


class EvidenceLedger:
    """Thread-safe JSONL append ledger. Records are append-only by convention."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._lock = threading.Lock()

    def append(self, record: Mapping[str, Any]) -> str:
        safe = _redact(dict(record))
        canonical = json.dumps(safe, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        entry = {"evidence_id": digest, **safe}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(entry, sort_keys=True, separators=(",", ":"))
        with self._lock:
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(line + "\n")
                handle.flush()
                os.fsync(handle.fileno())
        return digest

    def read(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        records = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    records.append(json.loads(line))
        return records


class PluginRegistry:
    """In-memory adapter registry; provider auth remains outside this package."""

    def __init__(self):
        self._adapters: dict[str, Adapter] = {}

    def register(self, adapter: Adapter) -> None:
        key = adapter.adapter_id.strip().lower()
        if not key or key in self._adapters:
            raise ValueError(f"Invalid or duplicate adapter id: {key!r}")
        self._adapters[key] = adapter

    def discover(self) -> dict[str, tuple[str, ...]]:
        return {
            key: tuple(sorted(adapter.capabilities().keys()))
            for key, adapter in sorted(self._adapters.items())
        }

    def get(self, adapter_id: str) -> Adapter:
        try:
            return self._adapters[adapter_id.strip().lower()]
        except KeyError as exc:
            raise KeyError(f"Adapter not registered: {adapter_id}") from exc


class PluginRuntime:
    """Execute injected adapters through common policy and evidence rules."""

    def __init__(self, registry: PluginRegistry, ledger: EvidenceLedger,
                 max_attempts: int = 2, base_delay_seconds: float = 0.05,
                 sleeper: Callable[[float], None] = time.sleep):
        if max_attempts < 1 or max_attempts > 5:
            raise ValueError("max_attempts must be between 1 and 5")
        if base_delay_seconds < 0:
            raise ValueError("base_delay_seconds cannot be negative")
        self.registry = registry
        self.ledger = ledger
        self.max_attempts = max_attempts
        self.base_delay_seconds = base_delay_seconds
        self._sleep = sleeper

    def execute(self, adapter_id: str, capability_name: str,
                payload: Mapping[str, Any], context: ExecutionContext) -> ExecutionResult:
        adapter = self.registry.get(adapter_id)
        capabilities = adapter.capabilities()
        if capability_name not in capabilities:
            raise KeyError(f"Capability not advertised: {capability_name}")
        capability = capabilities[capability_name]

        if capability.approval != ApprovalClass.READ and not context.approved:
            return self._record(
                Outcome.BLOCKED, adapter_id, capability_name, context.target,
                0, "Explicit approval required for this operation.",
            )
        if not capability.idempotent and self.max_attempts > 1:
            attempts_limit = 1
        else:
            attempts_limit = self.max_attempts

        attempts = 0
        last_error = ""
        while attempts < attempts_limit:
            attempts += 1
            try:
                value = adapter.execute(capability_name, payload, context)
                if capability.approval == ApprovalClass.READ:
                    return self._record(
                        Outcome.VERIFIED, adapter_id, capability_name,
                        context.target, attempts, "Read operation completed.",
                        value=value,
                    )
                if capability.verify_after_write:
                    verified = adapter.verify(
                        capability_name, payload, value, context
                    )
                    if not verified:
                        return self._record(
                            Outcome.UNVERIFIED, adapter_id, capability_name,
                            context.target, attempts,
                            "Write returned but read-after-write verification failed.",
                            value=value,
                        )
                    return self._record(
                        Outcome.VERIFIED, adapter_id, capability_name,
                        context.target, attempts,
                        "Write completed and read-after-write verification passed.",
                        value=value,
                    )
                return self._record(
                    Outcome.SUCCEEDED, adapter_id, capability_name,
                    context.target, attempts,
                    "Write completed; adapter does not support verification.",
                    value=value,
                )
            except RetryableAdapterError as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                if attempts < attempts_limit:
                    self._sleep(self.base_delay_seconds * (2 ** (attempts - 1)))
            except Exception as exc:  # auth, validation, and unknown errors are not retried
                last_error = f"{type(exc).__name__}: {exc}"
                break

        return self._record(
            Outcome.FAILED, adapter_id, capability_name, context.target,
            attempts, last_error,
        )

    def _record(self, outcome: Outcome, adapter: str, capability: str,
                target: str, attempts: int, message: str,
                value: Any = None) -> ExecutionResult:
        evidence_id = self.ledger.append({
            "outcome": outcome.value,
            "adapter": adapter,
            "capability": capability,
            "target": target,
            "attempts": attempts,
            "message": message,
            "value": value,
        })
        return ExecutionResult(
            outcome=outcome, adapter=adapter, capability=capability,
            target=target, attempts=attempts, value=value,
            evidence_id=evidence_id, message=message,
        )
