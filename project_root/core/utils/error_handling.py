from functools import wraps
from typing import Any, Callable

from .logging import get_logger

logger = get_logger(__name__)


class NexusError(Exception):
    """Base exception for all Nexus system errors."""

    def __init__(self, message: str, code: str = "NEXUS_ERR") -> None:
        super().__init__(message)
        self.code = code


class AgentError(NexusError):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="AGENT_ERR")


class SandboxError(NexusError):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="SANDBOX_ERR")


class ProtocolError(NexusError):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="PROTOCOL_ERR")


def safe_execute(fn: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return fn(*args, **kwargs)
        except NexusError:
            raise
        except Exception as exc:
            logger.error("Unhandled error in %s: %s", fn.__name__, exc)
            raise NexusError(str(exc)) from exc

    return wrapper
