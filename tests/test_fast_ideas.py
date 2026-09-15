import json, subprocess, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
EXP = REPO/"lab"/"experiments"
PY = sys.executable
def run(n,*a):
    p=EXP/n
    if not p.exists(): return None
    r=subprocess.run([PY,str(p),*a],capture_output=True,text=True,timeout=35)
    assert r.returncode==0
    return json.loads(r.stdout)
def test_sigil():
    j=run("sigil_clock.py")
    if j: assert j["ok"] and j.get("sigil")
def test_entropy():
    j=run("entropy_meter.py")
    if j: assert j["ok"] and "entropy" in j
def test_census():
    j=run("wave_census.py")
    if j: assert j["ok"]
def test_splice():
    j=run("caption_splice.py")
    if j: assert j["ok"] and len(j["frames"])==4
def test_fast_board():
    j=run("fast_board.py")
    if j: assert j["passed"]>=4
