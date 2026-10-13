from __future__ import annotations

def test_silence_border_status():
    from api.wave952_silence_border import handler, coherence_vitals
    result = handler({"action": "status"})
    assert result["wave"] == 952
    assert result["surface"] == "silence"
    assert result["audio"] is False
    assert "payload" not in result or result.get("payload") is None
    vitals = coherence_vitals()
    assert vitals["ok"] is True


def test_silence_border_action():
    from api.wave952_silence_border import handler
    result = handler({"action": "border", "width": 2})
    assert result["status"] == "bordered"
    assert result["border"] == 2
    assert result["audio"] is False
    assert result["surface"] == "silence"
    assert result.get("payload") is None


def test_resonates_with():
    from api.wave952_silence_border import resonates_with
    rs = resonates_with()
    assert "wave950_hush_margin" in rs
    assert isinstance(rs, list)
