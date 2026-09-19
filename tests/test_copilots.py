"""Co-pilot council tests."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lab.ops.copilots.aegis import Aegis
from lab.ops.copilots.helix import Helix
from lab.ops.copilots.quill import Quill
from lab.ops.copilots.council import run_council


def test_aegis_scan():
    r = Aegis().scan_local()
    assert r["agent"] == "AEGIS"
    assert r["posture"] in ("green", "amber", "red")
    assert r["checks"]


def test_helix_growth():
    h = Helix()
    b = h.growth_brief()
    assert b["next"]["wave"] >= 1
    assert b["next"]["module"].startswith("wave")


def test_quill_brief():
    q = Quill()
    b = q.brief(extra="test")
    assert b["caption"]["style"] == "silent_caption_only"
    assert "doctrine" in b


def test_council():
    p = run_council()
    assert p["council"] == ["AEGIS", "HELIX", "QUILL"]
    assert p["alongside"] == "ALEPH"
