import json, subprocess, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
EXP = REPO / "lab" / "experiments"
PY = sys.executable
def run(n, *a):
    p = EXP / n
    if not p.exists(): return None
    r = subprocess.run([PY, str(p), *a], capture_output=True, text=True, timeout=50)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)
def test_ghost_routes():
    j = run("ghost_route_finder.py")
    if j: assert j["ok"] and "ghosts" in j
def test_doctrine_pulse():
    j = run("doctrine_pulse.py")
    if j: assert j["ok"] and j.get("line")
def test_hex_altar():
    j = run("hex_altar.py")
    if j: assert j["ok"] and j.get("hash")
