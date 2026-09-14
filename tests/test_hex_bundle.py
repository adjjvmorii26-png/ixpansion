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


BUNDLE = REPO / "lab" / "experiments" / "organism_bundle.hexsrc"


def _segments():
    if not BUNDLE.exists():
        return []
    text = BUNDLE.read_text()
    parts, current = [], None
    for ln in text.splitlines():
        if ln.startswith("; ---- ") and ln.endswith(" ----"):
            if current is not None:
                parts.append(current)
            current = [ln]
        elif current is not None:
            current.append(ln)
    if current is not None:
        parts.append(current)
    return ["\n".join(seg) for seg in parts]


def test_every_bundle_segment_runs_on_runtime():
    segs = _segments()
    if not segs:
        return
    sys.path.insert(0, str(REPO))
    from api.wave97_hex_runtime import HexProgram, HexRuntime
    for seg in segs:
        prog = HexProgram(seg)
        assert prog.parse() is True, f"{seg[:40]}... -> {prog.error}"
        result = HexRuntime().run(prog)
        assert result["ok"] is True


def test_bundle_hash_matches_content():
    if not BUNDLE.exists() or not (REPO / "lab" / "experiments" / "hex_bundle.py").exists():
        return
    import hashlib
    text = BUNDLE.read_text()
    first = text.splitlines()[0]
    body = "\n".join(text.splitlines()[1:]) + "\n"
    expected = hashlib.sha256(body.encode()).hexdigest()[:16]
    assert expected in first
