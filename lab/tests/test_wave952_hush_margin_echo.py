"""Wave 952 — hush_margin_echo

Lab organ. Dual-track: lab gates ≠ ALEPH CI.
Echoes the silent margin of a 12-char witness into a residual slot.
Payload stays empty. Silence is the product surface.

Resonates with wave950_hush_margin, wave949_council_witness.
"""
from __future__ import annotations

def handler(action: str, payload: dict | None = None) -> dict:
    """Minimal handler for margin echo."""
    if action == "echo":
        token = (payload or {}).get("token", "")
        margin = max(0, 12 - len(token))
        return {"echoed": margin == 0, "slot": "E0001" if margin else "", "surface": ""}
    return {"ok": True, "action": action}

def coherence_vitals() -> dict:
    return {"stable": True, "margin_echo": 1, "silence": True}

def resonates_with() -> list[str]:
    return ["wave950_hush_margin", "wave949_council_witness"]

def test_handler_echo_full_margin():
    result = handler("echo", {"token": "ABCDEFGHIJKL"})
    assert result["echoed"] is True
    assert result["slot"] == "E0001"
    assert result["surface"] == ""

def test_handler_echo_short_empty():
    result = handler("echo", {"token": "ABC"})
    assert result["echoed"] is False
    assert result["slot"] == ""
    assert result["surface"] == ""

def test_coherence_vitals():
    v = coherence_vitals()
    assert v["stable"] is True
    assert v["silence"] is True

def test_resonates_with():
    r = resonates_with()
    assert "wave950_hush_margin" in r
    assert "wave949_council_witness" in r
