"""CLI tests for hexrun — run .hexsrc files, raw bytecode, and bundles."""
import json, subprocess, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
PY = sys.executable


def run_cli(*args):
    r = subprocess.run([PY, str(REPO / "cli.py"), *args], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def test_default_sample():
    j = run_cli("hexrun")
    assert j["action"] == "hex_run_operation"
    assert j["halted"] is True


def test_src_file():
    src = REPO / "lab" / "experiments" / "consent_program.hexsrc"
    if not src.exists():
        return
    j = run_cli("hexrun", "--src", str(src))
    assert j["action"] == "hex_run_file"
    assert j["result"]["ok"] is True


def test_raw_bytecode():
    j = run_cli("hexrun", "--raw", "1005100320ff")
    assert j["action"] == "hex_run_raw"
    assert j["result"]["stack"] == [8]


def test_bundle_segments():
    bundle = REPO / "lab" / "experiments" / "organism_bundle.hexsrc"
    if not bundle.exists():
        return
    j = run_cli("hexrun", "--bundle", str(bundle))
    assert j["action"] == "hex_run_bundle"
    assert j["segments"] >= 2
    assert all(r["ok"] for r in j["runs"])


def test_missing_file():
    j = run_cli("hexrun", "--src", "does_not_exist.hexsrc")
    assert j["ok"] is False
    assert "not found" in j["error"]
