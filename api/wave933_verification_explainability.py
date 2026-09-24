"""Wave 933 — Verification Explainability.

Produces a deterministic, descriptive explanation of a Wave 932 verification result.
This layer does not judge correctness; it explains the observed comparison.
"""
from __future__ import annotations
from typing import Any, Dict

def explain(verification: Dict[str, Any]) -> Dict[str, Any]:
    match = verification.get("match") is True
    expected = verification.get("expected_fingerprint")
    provided = verification.get("provided_fingerprint")
    if match:
        finding = "fingerprints_match"
    else:
        finding = "fingerprints_differ"
    return {
        "wave": 933,
        "finding": finding,
        "expected_present": expected is not None,
        "provided_present": provided is not None,
        "match": match,
        "interpretation": "descriptive_verification_explanation_only",
    }

def handler(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    action = payload.get("action", "status")
    if action == "explain":
        return explain(payload.get("verification", {}))
    if action == "status":
        return {"wave": 933, "name": "verification_explainability", "status": "experimental"}
    return {"error": "unknown action", "available": ["status", "explain"]}

def coherence_vitals() -> dict:
    return {"layer": "experimental", "status": "active", "wave": "933", "module": "verification_explainability"}

def resonates_with() -> list:
    return ["wave932_window_verification", "wave931_window_integrity"]
