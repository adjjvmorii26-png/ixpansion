"""Global test configuration — restores data/*.json to committed baseline.

Some wave modules persist state in data/*.json. Between test runs,
stale counts accumulate and break tests that assert exact values.
This conftest restores all tracked data files before collection so
module imports see clean state.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def pytest_configure(config):
    """Restore data/*.json from git before any imports happen."""
    subprocess.run(
        ["git", "checkout", "--", "data/"],
        cwd=str(ROOT), capture_output=True, timeout=30,
    )
