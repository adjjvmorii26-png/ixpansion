from api.wave952_council_pulse_vitals import handler, coherence_vitals, resonates_with


def test_status_is_silent_and_dual_track():
    out = handler()
    assert out["wave"] == 952
    assert out["audio"] is None
    assert out["surface"] == "silence"
    assert out["dual_track"] is True
    assert "AEGIS" in out["council"]


def test_vitals_and_resonance():
    v = coherence_vitals()
    assert v["wave"] == "952"
    assert v["audio"] is None
    assert "wave770_copilot_council_pulse" in resonates_with()
    assert "error" in handler({"action": "unknown"})
