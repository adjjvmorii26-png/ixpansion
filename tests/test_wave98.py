"""Tests for Wave 98 — HEX Cathedral Lacery."""
from __future__ import annotations
import json
import tempfile
from pathlib import Path

import pytest
from api.wave98_hex_cathedral import (
    HexCathedral,
    handler,
    coherence_vitals,
    DEFAULT_BUNDLE,
    _split_bundle,
)


class TestSplitBundle:
    def test_two_chapels(self):
        src = "; ---- a ----\nPUSH 1\n; ---- b ----\nPUSH 2"
        segs = _split_bundle(src)
        assert len(segs) == 2
        assert segs[0][0] == "a"
        assert segs[1][0] == "b"

    def test_empty(self):
        assert _split_bundle("") == []


class TestHexCathedralLace:
    def test_default_bundle_laces(self):
        cat = HexCathedral()
        assert cat.lace(DEFAULT_BUNDLE) is True
        assert len(cat.chapels) == 2
        assert "consent_chapel" == cat.chapels[0]["name"]
        assert "mercy_chapel" == cat.chapels[1]["name"]
        assert cat.error is None

    def test_altars_declared(self):
        cat = HexCathedral()
        assert cat.lace(DEFAULT_BUNDLE)
        assert "consent_hall" in cat.altars
        assert "refuse_rite" in cat.altars
        assert cat.altars["consent_hall"]["chapel"] == "consent_chapel"

    def test_cross_chapel_laces(self):
        cat = HexCathedral()
        assert cat.lace(DEFAULT_BUNDLE)
        links = {l["label"]: l for l in cat.laces}
        assert "consent_hall" in links
        assert links["consent_hall"]["from"] == "mercy_chapel"
        assert links["consent_hall"]["to"] == "consent_chapel"

    def test_unknown_altar_fails(self):
        src = "; ---- a ----\nJMPZ @missing\nHALT"
        cat = HexCathedral()
        assert cat.lace(src) is False
        assert "unknown altar" in (cat.error or "")

    def test_duplicate_altar_fails(self):
        src = "; ---- a ----\n; #altar x\nHALT\n; #altar x\nHALT"
        cat = HexCathedral()
        assert cat.lace(src) is False
        assert "duplicate altar" in (cat.error or "")

    def test_non_jmpz_at_label_fails(self):
        src = "; ---- a ----\n; #altar x\nGLYPH @x\nHALT"
        cat = HexCathedral()
        assert cat.lace(src) is False
        assert "cannot take an @altar label" in (cat.error or "")

    def test_flattened_has_jmpz_resolved(self):
        cat = HexCathedral()
        assert cat.lace(DEFAULT_BUNDLE)
        # mercy's JMPZ @consent_hall should be resolved to an absolute line
        resolved = [i for i in cat.flattened if i[0] == "JMPZ"]
        assert len(resolved) == 1
        assert resolved[0][1] is not None
        # target must be inside consent_chapel
        consent = cat.chapels[0]
        assert consent["line_start"] <= resolved[0][1] < consent["line_end"]


class TestHexCathedralRun:
    def test_run_mercy_jumps_to_consent(self):
        cat = HexCathedral()
        assert cat.lace(DEFAULT_BUNDLE)
        result = cat.run()
        assert result["ok"] is True
        assert result["halted"] is True
        # Mercy's JMPZ landed at consent_hall -> GLYPH emitted
        assert len(result["glyphs"]) >= 1
        # ENACT from consent chapel executed
        enact = [e for e in result["trace"] if e["op"] == "ENACT"]
        assert len(enact) >= 1

    def test_chapel_heat_recorded(self):
        cat = HexCathedral()
        assert cat.lace(DEFAULT_BUNDLE)
        result = cat.run()
        heat = result["chapel_heat"]
        assert "consent_chapel" in heat or "mercy_chapel" in heat

    def test_laces_in_result(self):
        cat = HexCathedral()
        assert cat.lace(DEFAULT_BUNDLE)
        result = cat.run()
        assert len(result["laces"]) > 0


class TestCoherenceVitals:
    def test_wave(self):
        v = coherence_vitals()
        assert v["wave"] == 98
        assert v["chapels"] > 0
        assert v["laces"] > 0


class TestHandler:
    def test_status(self):
        out = handler({"action": "status"})
        assert out["action"] == "status"
        assert out["wave"] == 98
        assert out["chapels"] > 0

    def test_lace(self):
        out = handler({"action": "lace"})
        assert out["action"] == "lace"
        assert out["wave"] == 98
        assert out["chapels"] == ["consent_chapel", "mercy_chapel"]
        assert "consent_hall" in str(out["altars"])

    def test_run(self):
        out = handler({"action": "run"})
        assert out["action"] == "run"
        assert out["result"]["ok"] is True
        assert out["result"]["halted"] is True

    def test_reset(self):
        out = handler({"action": "reset"})
        assert out["action"] == "reset"
        assert out["message"] == "Cathedral reset"

    def test_history(self):
        handler({"action": "reset"})
        handler({"action": "run"})
        out = handler({"action": "history"})
        assert out["action"] == "history"
        assert isinstance(out["history"], list)

    def test_unknown_action(self):
        out = handler({"action": "bogus"})
        assert out["ok"] is False
