"""Wave 406 — Temporal Lineage Gate.

Gatekeeper for temporal lineage integrity. Ensures all evolution
events maintain causal consistency across time. Validates that
mutations respect temporal ordering and that lineage branches
remain coherent.
"""
from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict, List, Optional, Tuple


class TemporalLineageGate:
    """Validates and gates temporal lineage operations."""

    def __init__(self):
        self.timeline: List[Dict] = []
        self.paradox_records: List[Dict] = []
        self.gate_state = "OPEN"
        self.last_validation = time.time()

    def validate_event(self, event: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate an event against temporal lineage rules."""
        timestamp = event.get("timestamp", time.time())
        parent = event.get("parent_id")

        # Check temporal ordering
        if self.timeline and timestamp < self.timeline[-1].get("timestamp", 0):
            self._record_paradox(event, "TEMPORAL_INVERSION")
            return False, "TEMPORAL_INVERSION: event precedes last recorded event"

        # Check causality
        if parent:
            parent_found = any(e.get("id") == parent for e in self.timeline)
            if not parent_found and len(self.timeline) > 0:
                self._record_paradox(event, "CAUSALITY_BREAK")
                return False, "CAUSALITY_BREAK: parent not found in lineage"

        self.timeline.append(event)
        self.last_validation = time.time()
        return True, "VALIDATED"

    def _record_paradox(self, event: Dict, paradox_type: str):
        self.paradox_records.append({
            "event_id": event.get("id", "unknown"),
            "type": paradox_type,
            "timestamp": time.time(),
            "event": event,
        })
        if len(self.paradox_records) > 100:
            self.gate_state = "LOCKED"

    def get_lineage_status(self) -> Dict[str, Any]:
        return {
            "gate_state": self.gate_state,
            "timeline_depth": len(self.timeline),
            "paradox_count": len(self.paradox_records),
            "last_validation": self.last_validation,
            "coherent": self.gate_state == "OPEN",
        }

    def reconcile(self) -> Dict[str, Any]:
        """Attempt to reconcile paradox records."""
        resolved = 0
        for p in self.paradox_records:
            if p["type"] == "TEMPORAL_INVERSION":
                # Sort timeline by timestamp to fix ordering
                self.timeline.sort(key=lambda e: e.get("timestamp", 0))
                resolved += 1
        self.paradox_records = []
        self.gate_state = "OPEN"
        return {"resolved": resolved, "gate_state": self.gate_state}


_gate = None

def get_gate() -> TemporalLineageGate:
    global _gate
    if _gate is None:
        _gate = TemporalLineageGate()
    return _gate

def handler(query: Dict[str, Any] = None) -> Dict[str, Any]:
    gate = get_gate()
    q = query or {}

    if "action" not in q:
        return {"module": "temporal_lineage_gate", **gate.get_lineage_status()}

    action = q["action"]
    if action == "validate":
        event = json.loads(q.get("event", "{}"))
        valid, reason = gate.validate_event(event)
        return {"valid": valid, "reason": reason}
    elif action == "reconcile":
        result = gate.reconcile()
        return {"reconciliation": result}
    elif action == "status":
        return gate.get_lineage_status()
    else:
        return {"error": f"unknown action: {action}"}
