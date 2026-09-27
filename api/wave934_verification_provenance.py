"""Wave 934 — Verification Provenance.

Adds deterministic source metadata to Wave 933 explanations.
This layer records provenance of the observed explanation only; it does not
establish correctness, truth, authenticity, or causation.
"""
from __future__ import annotations
from typing import Any, Dict

def provenance(explanation: Dict[str, Any]) -> Dict[str, Any]:
    fields = [
        "wave",
        "finding",
        "expected_present",
        "provided_present",
        "match",
        "interpretation",
    ]
    present = [name for name in fields if name in explanation]
    missing = [name for name in fields if name not in explanation]
    return {
        "wave": 934,
        "source_wave": explanation.get("wave"),
        "source_fields_present": present,
        "source_fields_missing": missing,
        "source_field_count": len(present),
        "interpretation": "descriptive_provenance_only",
    }

def handler(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    action = payload.get("action", "status")
    if action == "provenance":
        return provenance(payload.get("explanation", {}))
    if action == "status":
        return {"wave": 934, "name": "verification_provenance", "status": "experimental"}
    return {"error": "unknown action", "available": ["status", "provenance"]}

def coherence_vitals() -> dict:
    return {
        "layer": "experimental",
        "status": "active",
        "wave": "934",
        "module": "verification_provenance",
    }

def resonates_with() -> list:
    return ["wave933_verification_explainability", "wave932_window_verification"]
