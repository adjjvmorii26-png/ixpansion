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
