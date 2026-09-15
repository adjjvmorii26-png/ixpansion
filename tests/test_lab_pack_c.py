import json, subprocess, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
EXP = REPO / "lab" / "experiments"
PY = sys.executable
def run(n, *a):
    p = EXP / n
    if not p.exists(): return None
    r = subprocess.run([PY, str(p), *a], capture_output=True, text=True, timeout=40)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)
def test_choir():
    j = run("resonant_hash_choir.py", "altar")
    if j: assert j["ok"] and len(j["chord"]) == 3
def test_fold_needle():
    j = run("fold_pressure_needle.py")
    if j: assert j["ok"] and j["pressure"] >= 0
def test_epoch_coin():
    j = run("epoch_coin.py")
    if j: assert j["face"] in ("EXPAND", "COMPACT")
def test_mycelial():
    j = run("mycelial_links.py")
    if j: assert j["ok"] and "links" in j
