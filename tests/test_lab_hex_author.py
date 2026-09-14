"""Tests for hex_author — decisions compile into runnable HEX programs."""
import json, subprocess, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
EXP = REPO / "lab" / "experiments"
PY = sys.executable


def run_author(*args):
    p = EXP / "hex_author.py"
    r = subprocess.run([PY, str(p), *args], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def test_author_emits_and_runs():
    j = run_author()
    assert j["ok"] is True
    assert len(j["scripts"]) == 3
    for s in j["scripts"]:
        assert s["run"]["ok"] is True
        assert s["bytecode"]


def test_consent_guard_refuses_denied_scopes():
    j = run_author()
    guard = next(s for s in j["scripts"] if s["name"] == "consent_guard")
    assert guard["n_denied"] > 0
    assert guard["run"]["enactments"] == [guard["n_denied"]]


def test_mercy_allow_path():
    j = run_author()
    allow = next(s for s in j["scripts"] if s.get("task", "").startswith("run survey"))
    assert allow["allow"] is True
    assert len(allow["run"]["enactments"]) == 1
    assert allow["run"]["glyphs"][0].endswith("glyph_19")


def test_mercy_refuse_path():
    j = run_author()
    refuse = next(s for s in j["scripts"] if "delete ci" in s.get("task", ""))
    assert refuse["allow"] is False
    assert refuse["run"]["glyphs"][0].endswith("glyph_0")
    assert refuse["run"]["enactments"] == [0]


def test_bytecode_parses_in_runtime():
    import sys as _sys
    _sys.path.insert(0, str(REPO))
    from api.wave97_hex_runtime import HexProgram, HexRuntime
    from lab.experiments.hex_author import emit_consent_guard, emit_mercy_check, load_consent
    script = emit_consent_guard(load_consent())
    prog = HexProgram(script["bytecode"])
    assert prog.parse() is True, prog.error
    result = HexRuntime().run(prog)
    assert result["ok"] is True
