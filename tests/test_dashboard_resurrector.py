"""Tests for dashboard_resurrector (Wave 99)."""
from __future__ import annotations
import sys
import tempfile
from pathlib import Path
from lab.experiments.dashboard_resurrector import needs_resurrection, resurrect, main


def test_needs_resurrection_true(tmp_path: Path):
    html = tmp_path / "stale.html"
    html.write_text("<html><body></body></html>")
    assert needs_resurrection(html) is True


def test_needs_resurrection_false(tmp_path: Path):
    html = tmp_path / "alive.html"
    html.write_text("<html><body><script>fetch('/api/')</script></body></html>")
    assert needs_resurrection(html) is False


def test_resurrect(tmp_path: Path):
    html = tmp_path / "stale.html"
    html.write_text("<html><body></body></html>")
    resurrect(html)
    text = html.read_text()
    assert "organism:data" in text
    assert "</body>" in text


def test_dry_run():
    sys.argv = ["dashboard_resurrector.py", "--dry-run"]
    assert main() is None
