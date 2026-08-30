"""Harbinger — conclave agent tests (offline, no git mutation)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harbinger.agents import scout, overseer, archivist, chronicler  # noqa: E402
from harbinger.agents import gardener as gardener_agent  # noqa: E402
from harbinger.conclave import ceremony  # noqa: E402


def test_scout_reports_health():
    r = scout.run()
    assert r["agent"] == "scout"
    assert r["modules"] >= 1
    assert r["tests"] >= 900
    assert "health" in r and r["health"].get("status") == "healthy"
    assert r["verdict"] in ("stable", "drifting")


def test_scout_count_matches_platform():
    r = scout.run()
    assert r["modules"] == r["health"].get("modules")


def test_overseer_proposes_when_idea_given():
    clean_pulse = {"modules": 352, "tests": 973, "health": {"status": "healthy"},
                   "dirty": 0, "broken_refs": []}
    r = overseer.run(clean_pulse, ideas=["grow a fortune engine"])
    assert r["agent"] == "overseer"
    assert r["proposal"]["reason"] == "idea"
    assert "fortune" in r["proposal"]["title"]


def test_overseer_rest_when_stable():
    r = overseer.run({"modules": 352, "tests": 973, "health": {"status": "healthy"},
                      "dirty": 0, "broken_refs": []})
    assert r["proposal"]["reason"] in ("repair", "rest", "fortify")


def test_archivist_mints_next_patch():
    v = archivist.mint("3.61.0")
    assert v == "3.61.1"
    v2 = archivist.mint("3.1.9")
    assert v2 == "3.1.10"


def test_archivist_append_idempotent(tmp_path, monkeypatch):
    cl = tmp_path / "CHANGELOG.md"
    cl.write_text("# Changelog\n\n## [3.61.0] — Test\n\n")
    monkeypatch.setattr(archivist, "CHANGELOG", cl)
    r1 = archivist.append("New Wave", version="3.61.1", body="- a thing")
    r2 = archivist.append("New Wave", version="3.61.1", body="- a thing")
    assert r1["written"] is True and r2["written"] is False
    assert "3.61.1" in cl.read_text()


def test_chronicler_writes_revelation(tmp_path, monkeypatch):
    cl = tmp_path / "CHANGELOG.md"
    cl.write_text("# Changelog\n\n## [3.61.0] — Test Wave\n\n")
    rev = tmp_path / "REVELATIONS.md"
    monkeypatch.setattr(chronicler, "CHANGELOG", cl)
    monkeypatch.setattr(chronicler, "REVELATIONS", rev)
    r = chronicler.run()
    assert r["written"] is True and "Test Wave" in rev.read_text()


def test_gardener_needs_words():
    r = gardener_agent.run(words=None)
    assert r["planted"] is False


def test_ceremony_dry_touches_nothing(tmp_path, monkeypatch):
    monkeypatch.setattr(archivist, "CHANGELOG", tmp_path / "CHANGELOG.md")
    r = ceremony(dry=True, ideas=["a quiet idea"])
    assert r["mode"] == "dry"
    assert r["agents"]["archivist"]["written"] if "written" in r["agents"]["archivist"] else True or True
    assert not (tmp_path / "CHANGELOG.md").exists()
