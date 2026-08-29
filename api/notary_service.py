"""Wave 136 — Notary Service.

Attests and timestamps digital events with a signed notary seal. Any
state change, contract, or artifact can be notarized, producing a
verifiable witness record that proves an event happened at a given
moment — the trust layer for the whole civilization.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List


class NotarizedRecord:
    """A signed, timestamped witness of an event."""

    def __init__(self, subject: str, kind: str):
        self.subject = subject
        self.kind = kind
        self.timestamp = time.time()
        self.seal = ""
        self.created = time.time()
        self.id = hashlib.sha256(f"notary:{subject}:{kind}".encode()).hexdigest()[:10]

    def sign(self, verifier_key: str) -> str:
        self.seal = hashlib.sha256(
            f"{self.id}:{self.subject}:{self.kind}:{self.timestamp:.6f}:{verifier_key}".encode()
        ).hexdigest()
        return self.seal

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "subject": self.subject, "kind": self.kind,
                "timestamp": round(self.timestamp, 6), "seal": self.seal[:20]}


class NotaryService:
    """Attests and verifies signed witnesses of events."""

    def __init__(self, verifier_key: str = "civilization"):
        self.verifier_key = verifier_key
        self._records: Dict[str, NotarizedRecord] = {}
        self._seals = 0

    def notarize(self, subject: str, kind: str) -> NotarizedRecord:
        record = NotarizedRecord(subject, kind)
        record.sign(self.verifier_key)
        self._records[record.id] = record
        self._seals += 1
        return record

    def verify(self, record_id: str) -> bool:
        record = self._records.get(record_id)
        if record is None:
            return False
        expected = hashlib.sha256(
            f"{record.id}:{record.subject}:{record.kind}:{record.timestamp:.6f}:{self.verifier_key}".encode()
        ).hexdigest()
        return record.seal == expected

    def records_by_kind(self, kind: str) -> List[Dict[str, Any]]:
        return [r.to_dict() for r in self._records.values() if r.kind == kind]

    def status(self) -> Dict[str, Any]:
        return {"records": len(self._records), "seals": self._seals,
                "verifier": self.verifier_key}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    notary = NotaryService()
    return {"status": "active", "module": "notary_service",
            **notary.status()}
