"""Wave 125 — Digital Immune System.

Protects the system from errors, anomalies, and hostile inputs using
biological immune strategies — detection, response, memory, and
adaptation. The system learns from past infections.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional


class ImmuneResponse:
    """A recorded immune response to a threat."""

    def __init__(self, threat_type: str, severity: float):
        self.threat_type = threat_type
        self.severity = severity
        self.detected_at = time.time()
        self.resolved = False
        self.resolution_time: Optional[float] = None
        self.id = hashlib.sha256(f"immune:{threat_type}:{self.detected_at}".encode()).hexdigest()[:10]

    def resolve(self) -> float:
        self.resolved = True
        self.resolution_time = time.time() - self.detected_at
        return self.resolution_time

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "threat": self.threat_type,
                "severity": round(self.severity, 4), "resolved": self.resolved}


class DigitalImmuneSystem:
    """Biological immune system for code."""

    def __init__(self):
        self._responses: List[ImmuneResponse] = []
        self._antibodies: Dict[str, int] = {}
        self._threshold = 0.5

    def detect(self, threat_type: str, severity: float) -> Dict[str, Any]:
        response = ImmuneResponse(threat_type, severity)
        self._responses.append(response)
        if severity >= self._threshold:
            self._neutralise(response)
            return {"detected": True, "severity": round(severity, 4),
                    "response_id": response.id}
        return {"detected": False, "severity": round(severity, 4)}

    def _neutralise(self, response: ImmuneResponse) -> None:
        response.resolve()
        self._antibodies[response.threat_type] = self._antibodies.get(response.threat_type, 0) + 1

    def check_memory(self, threat_type: str) -> int:
        return self._antibodies.get(threat_type, 0)

    def status(self) -> Dict[str, Any]:
        resolved = sum(1 for r in self._responses if r.resolved)
        return {"total_responses": len(self._responses), "resolved": resolved,
                "unique_antibodies": len(self._antibodies)}


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    action = payload.get("action", "status")
    return {"status": "active", "module": "digital_immune_system", "action": action}
