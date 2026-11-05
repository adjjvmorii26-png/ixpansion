"""Regression checks for the HORTUS HEXIS dashboard's embedded JavaScript."""
import re
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = ROOT / "dashboard" / "hortus.html"


def test_hortus_dashboard_script_parses():
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is required to syntax-check embedded dashboard JavaScript")

    html = DASHBOARD.read_text(encoding="utf-8")
    scripts = re.findall(r"<script\\b[^>]*>(.*?)</script>", html, flags=re.IGNORECASE | re.DOTALL)
    assert scripts, "dashboard must contain an executable script"

    for index, script in enumerate(scripts):
        checked = subprocess.run(
            [node, "--check", "--input-type=commonjs"],
            input=script,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        assert checked.returncode == 0, f"script {index}: {checked.stderr}"


def test_hortus_metrics_are_explicitly_marked_as_simulated():
    html = DASHBOARD.read_text(encoding="utf-8")
    assert "SIMULATED INTERACTIVE VISUALIZATION" in html
    assert "Simulated Coherence" in html
    assert "Simulated Resonance" in html
    assert "Simulated Entropy" in html
    assert "Simulated Module Count" in html
