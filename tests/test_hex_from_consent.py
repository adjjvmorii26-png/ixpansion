import json, subprocess, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
p = REPO / "lab" / "experiments" / "hex_from_consent.py"
SRC = REPO / "lab" / "experiments" / "consent_program.hexsrc"


def test_hex_from_consent():
    if not p.exists():
        return
    r = subprocess.run([sys.executable, str(p)], capture_output=True, text=True, timeout=20)
    assert r.returncode == 0
    j = json.loads(r.stdout)
    assert j["ok"] and "GLYPH" in j.get("src_preview", "")


def test_consent_program_runs_on_wave97_runtime():
    if not SRC.exists() or not p.exists():
        return
    sys.path.insert(0, str(REPO))
    from api.wave97_hex_runtime import HexProgram, HexRuntime
    program = HexProgram(SRC.read_text())
    assert program.parse() is True, program.error
    result = HexRuntime().run(program)
    assert result["ok"] is True
    assert result["halted"] is True
    assert len(result["enactments"]) == 1  # ENACT executed
