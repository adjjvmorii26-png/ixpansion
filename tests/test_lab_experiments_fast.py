"""Fast tests for lab experiment toys."""
import json, subprocess, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
EXP = REPO / "lab" / "experiments"
PY = sys.executable
def run(script, *args):
    p = EXP / script
    if not p.exists():
        return None
    r = subprocess.run([PY, str(p), *args], capture_output=True, text=True, timeout=20)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)
def test_morse_ledger():
    j = run("morse_ledger.py", "ab")
    if j is None: return
    assert j["ok"] and "morse" in j
def test_orbit_count():
    j = run("orbit_count.py")
    if j is None: return
    assert j["ok"] and j["n"] >= 0
def test_quine_pulse():
    j = run("quine_pulse.py")
    if j is None: return
    assert j["ok"] and j.get("self_hash")
def test_tiny_vm_badge():
    j = run("tiny_vm.py", "A")
    if j is None: return
    assert j["ok"] and "badge" in j
def test_mercy_refuse_ci_delete():
    j = run("mercy_protocol.py", "delete ci workflow")
    if j is None: return
    assert j["ok"] and j.get("allow") is False
def test_compass_rose():
    j = run("compass_rose.py", "test")
    if j is None: return
    assert j["ok"] and j.get("bearing") in ("proof", "silence", "fold", "ceremony")
