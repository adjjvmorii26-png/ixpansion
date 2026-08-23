import pickle
from typing import Any

from core.utils.error_handling import ProtocolError


def dumps(data: Any) -> bytes:
    try:
        return pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as exc:
        raise ProtocolError(f"Binary encode failed: {exc}") from exc


def loads(raw: bytes) -> Any:
    try:
        return pickle.loads(raw)
    except Exception as exc:
        raise ProtocolError(f"Binary decode failed: {exc}") from exc
