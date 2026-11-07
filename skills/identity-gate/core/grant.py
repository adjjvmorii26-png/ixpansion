"""Host-keyed authorization grant signing and verification."""
from typing import Protocol
import hashlib
import hmac


class GrantAuthority(Protocol):
    def sign(self, payload: bytes) -> str: ...
    def verify(self, payload: bytes, signature: str) -> bool: ...


class HMACGrantAuthority:
    """HMAC-SHA256 grant authority; key material must be injected by the host."""
    def __init__(self, key: bytes):
        if not isinstance(key, bytes) or len(key) < 32:
            raise ValueError("grant signing key must contain at least 32 bytes")
        self._key = key

    def sign(self, payload: bytes) -> str:
        return hmac.new(self._key, payload, hashlib.sha256).hexdigest()

    def verify(self, payload: bytes, signature: str) -> bool:
        if not isinstance(signature, str) or not signature:
            return False
        expected = self.sign(payload)
        return hmac.compare_digest(expected, signature)
