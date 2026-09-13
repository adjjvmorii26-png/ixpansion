"""CF Bridge — Thin bridge to cf_portal.py ethics + boot + transition.

Additive only sync from main@7879dff. No wholesale branch merges.
"""
from __future__ import annotations

import json
from pathlib import Path

DATA = Path(__file__).parent.parent.parent / "data"
CF_PORTAL = Path(__file__).parent.parent / "CHRONOFORGE" / "runtime" / "cf_portal.py"


def ethics() -> dict:
    """Run ethics check through cf_portal."""
    import subprocess
    result = subprocess.run(
        ["python3", str(CF_PORTAL), "ethics"],
        capture_output=True, text=True,
    )
    return {
        "ethics": result.stdout.strip()[:200] if result.stdout else "no output",
        "returncode": result.returncode,
        "timestamp": time.time(),
    }


def boot() -> dict:
    """Boot cf_portal and return status."""
    import subprocess
    result = subprocess.run(
        ["python3", str(CF_PORTAL), "boot"],
        capture_output=True, text=True,
    )
    return {
        "boot": result.stdout.strip()[:200] if result.stdout else "no output",
        "returncode": result.returncode,
        "timestamp": time.time(),
    }


def transition_plan(step: str = "E2") -> dict:
    """Run transition plan through cf_portal."""
    import subprocess
    result = subprocess.run(
        ["python3", str(CF_PORTAL), "transition-plan", step],
        capture_output=True, text=True,
    )
    return {
        "transition": result.stdout.strip()[:200] if result.stdout else "no output",
        "step": step,
        "returncode": result.returncode,
        "timestamp": time.time(),
    }


def invariants() -> dict:
    """Run invariants check through cf_portal."""
    import subprocess
    result = subprocess.run(
        ["python3", str(CF_PORTAL), "invariants"],
        capture_output=True, text=True,
    )
    return {
        "invariants": result.stdout.strip()[:200] if result.stdout else "no output",
        "returncode": result.returncode,
        "timestamp": time.time(),
    }


def bridge_status() -> dict:
    """Full bridge status."""
    return {
        "ethics": ethics(),
        "boot": boot(),
        "transition_plan_E2": transition_plan("E2"),
        "invariants": invariants(),
        "timestamp": time.time(),
    }


if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    result = bridge_status()
    key = {"status": "bridge_status", "ethics": "ethics", "boot": "boot",
           "transition": "transition_plan_E2", "invariants": "invariants"}[action]
    print(json.dumps(result[key], indent=2))
