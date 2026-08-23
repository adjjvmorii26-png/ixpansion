import pickle
from typing import Any

from ...nucleus.utilities.exception_map import OmegaPrimeError


def dumps(data: Any) -> bytes:
    try:
        return pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as exc:
        raise OmegaPrimeError(f"binary encode: {exc}", "BIN_ENC")


def loads(raw: bytes) -> Any:
    try:
        return pickle.loads(raw)
    except Exception as exc:
        raise OmegaPrimeError(f"binary decode: {exc}", "BIN_DEC")
