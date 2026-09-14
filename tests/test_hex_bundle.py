import json, subprocess, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
p = REPO / "lab" / "experiments" / "hex_bundle.py"
def test_hex_bundle():
    if not p.exists(): return
    r = subprocess.run([sys.executable, str(p)], capture_output=True, text=True, timeout=40)
    assert r.returncode == 0
    j = json.loads(r.stdout)
    assert j["ok"] and j["segments"] >= 1 and j.get("hash")
