import json, subprocess, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
p = REPO / "lab" / "experiments" / "hex_from_consent.py"
def test_hex_from_consent():
    if not p.exists(): return
    r = subprocess.run([sys.executable, str(p)], capture_output=True, text=True, timeout=20)
    assert r.returncode == 0
    j = json.loads(r.stdout)
    assert j["ok"] and "GLYPH" in j.get("src_preview", "")
