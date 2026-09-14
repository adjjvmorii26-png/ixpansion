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
