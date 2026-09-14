"""Tests for the hexlace CLI command (Wave 98)."""
import json
import subprocess
import sys
from pathlib import Path

CLI = [sys.executable, "cli.py", "hexlace"]


def _run(*args):
    return json.loads(subprocess.run(CLI + list(args), capture_output=True, text=True, timeout=30).stdout)


def test_hexlace_default():
    out = _run()
    assert out["action"] == "lace"
    assert out["wave"] == 98
    assert out["chapels"] == ["consent_chapel", "mercy_chapel"]
    assert "consent_hall" in str(out["altars"])


def test_hexlace_src():
    p = Path("lab/experiments/organism_bundle.hexsrc")
    if p.exists():
        out = _run("--src", str(p))
        assert out["action"] == "lace"


def test_hexlace_message():
    out = _run()
    assert "Cathedral laced and lit" == out.get("message")
    assert out.get("run", {}).get("ok") is True
