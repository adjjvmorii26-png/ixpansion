import json, subprocess, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
p = REPO / "lab" / "experiments" / "hex_from_mercy.py"
def run(*args):
    r = subprocess.run([sys.executable, str(p), *args], capture_output=True, text=True, timeout=20)
    assert r.returncode == 0
    return json.loads(r.stdout)
def test_refuse_delete_ci():
    if not p.exists(): return
    j = run("delete ci workflow")
    assert j["refused"] is True and "JMPZ" in j["src_preview"]
def test_allow_survey():
    if not p.exists(): return
    j = run("run cartography survey")
    assert j["refused"] is False and "ENACT" in j["src_preview"]


def test_refuse_program_runs_and_skips_enact():
    if not p.exists():
        return
    src = REPO / "lab" / "experiments" / "mercy_program.hexsrc"
    subprocess.run([sys.executable, str(p), "delete ci workflow"], capture_output=True, timeout=20)
    assert src.exists()
    sys.path.insert(0, str(REPO))
    from api.wave97_hex_runtime import HexProgram, HexRuntime
    prog = HexProgram(src.read_text())
    assert prog.parse() is True, prog.error
    out = HexRuntime().run(prog)
    assert out["ok"] is True
    assert out["glyphs"] == ["\U0001f701glyph_0"]   # refuse artifact
    assert out["enactments"] == []                   # JMPZ skipped ENACT


def test_allow_program_enacts():
    if not p.exists():
        return
    src = REPO / "lab" / "experiments" / "mercy_program.hexsrc"
    subprocess.run([sys.executable, str(p), "run cartography survey"], capture_output=True, timeout=20)
    assert src.exists()
    sys.path.insert(0, str(REPO))
    from api.wave97_hex_runtime import HexProgram, HexRuntime
    prog = HexProgram(src.read_text())
    assert prog.parse() is True, prog.error
    out = HexRuntime().run(prog)
    assert out["ok"] is True
    assert len(out["enactments"]) == 1
