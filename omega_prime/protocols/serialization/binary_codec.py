"""Restricted pickle codec for trusted primitive payloads only.

Pickle is not a safe interchange format for untrusted bytes. This module
keeps the existing binary API while refusing global/class resolution during
loads, preventing arbitrary callable execution during deserialization.
"""
import io
import pickle
from typing import Any

from ...nucleus.utilities.exception_map import OmegaPrimeError


class _RestrictedUnpickler(pickle.Unpickler):
    """Unpickler that accepts primitive pickle data but no imported globals."""

    def find_class(self, module: str, name: str) -> Any:
        raise pickle.UnpicklingError(
            f"global object resolution is disabled ({module}.{name})"
        )

    def persistent_load(self, pid: Any) -> Any:
        raise pickle.UnpicklingError("persistent pickle references are disabled")


def dumps(data: Any) -> bytes:
    try:
        return pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as exc:
        raise OmegaPrimeError(f"binary encode: {exc}", "BIN_ENC")


def loads(raw: bytes) -> Any:
    """Decode primitive data only; never execute reducers or import globals."""
    try:
        if not isinstance(raw, bytes):
            raise TypeError("binary payload must be bytes")
        return _RestrictedUnpickler(io.BytesIO(raw)).load()
    except Exception as exc:
        raise OmegaPrimeError(f"binary decode: {exc}", "BIN_DEC")
