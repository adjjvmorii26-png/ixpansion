"""Tools smoke tests."""
from __future__ import annotations
import sys, subprocess, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

def test_entropy_sparkline_runs():
    r = subprocess.run(["python3", str(ROOT / "tools" / "entropy_sparkline.py")],
                       capture_output=True, text=True, timeout=30)
    assert r.returncode == 0
    assert "ENTROPY SPARKLINE" in r.stdout
    assert "commits" in r.stdout


def test_garden_family_tree_runs():
    r = subprocess.run(["python3", str(ROOT / "tools" / "garden_family_tree.py")],
                       capture_output=True, text=True, timeout=10)
    assert r.returncode == 0
    assert "FAMILY TREE" in r.stdout
    assert "organism" in r.stdout

def test_frontier_song_generates_notes():
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    from frontier_song import generate_notes, module_names, name_to_note
    names = module_names()
    assert len(names) > 100
    notes = generate_notes(names)
    assert len(notes) == len(names)
    f, d, v = name_to_note("test_module", 0)
    assert 100 < f <= 1760
    assert 0 < d <= 1 and 0 < v <= 1


def test_frontier_song_renders_wav(tmp_path):
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    from frontier_song import render_wav
    out = tmp_path / "t.wav"
    p = render_wav(["alpha_beta", "gamma_delta"], output=out)
    import wave
    w = wave.open(str(p))
    assert w.getnframes() > 0
    w.close()
