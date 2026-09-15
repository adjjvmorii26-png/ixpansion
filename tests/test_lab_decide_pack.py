import json, subprocess, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
EXP = REPO / "lab" / "experiments"
PY = sys.executable
def run(name, *a):
    p = EXP / name
    if not p.exists(): return None
    r = subprocess.run([PY, str(p), *a], capture_output=True, text=True, timeout=40)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)
def test_citizen_steward_enact():
    j = run("citizen_opcode.py", "steward", "enact census")
    if j: assert j["enact"] is True and "ENACT" in j["src_preview"]
def test_citizen_observer_no_enact():
    j = run("citizen_opcode.py", "observer", "enact census")
    if j: assert j["enact"] is False
def test_bloom_gate():
    j = run("proof_bloom_gate.py")
    if j: assert j["ok"] and j["decision"] in ("PUBLISH", "HOLD_ARCHIVE")
def test_promote_manifest():
    j = run("promote_manifest.py")
    if j: assert j["ok"] and "priority_present" in j
