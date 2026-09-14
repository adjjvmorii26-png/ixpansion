import json, subprocess, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
EXP = REPO / "lab" / "experiments"
PY = sys.executable
def run(name, *a):
    p = EXP / name
    if not p.exists(): return None
    r = subprocess.run([PY, str(p), *a], capture_output=True, text=True, timeout=25)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)
def test_proof_bloom():
    j = run("proof_bloom.py")
    if j: assert j["ok"] and "novel" in j
def test_route_cartograph():
    j = run("route_cartograph.py")
    if j: assert j["ok"] and j["api_n"] >= 0
def test_consent_lattice():
    j = run("consent_lattice.py")
    if j: assert j["ok"] and "denied" in j
