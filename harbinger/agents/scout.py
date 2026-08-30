"""Scout — the agent that takes the pulse of the frontier.

Surveys the monorepo: module and test counts, live health, dirty
files, recent commit cadence, and any broken references. The scout
never changes anything — it only reports.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]


def _run(cmd: List[str], cwd: Path = ROOT) -> str:
    try:
        proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=60)
        return (proc.stdout or "") + (proc.stderr or "")
    except Exception:
        return ""


def count_modules() -> int:
    api = ROOT / "api"
    if not api.exists():
        return 0
    return len([p for p in api.glob("*.py") if p.stem not in ("__init__", "index")])


def count_tests() -> int:
    tests = ROOT / "tests"
    if not tests.exists():
        return 0
    total = 0
    for f in tests.glob("test_*.py"):
        text = f.read_text(errors="replace")
        total += len(re.findall(r"^def test_|^    def test_", text, flags=re.MULTILINE))
    return total


def dirty_files() -> List[str]:
    out = _run(["git", "status", "--porcelain"])
    return [line[:200] for line in out.splitlines() if line.strip()]


def recent_commits(n: int = 8) -> List[Dict[str, str]]:
    out = _run(["git", "log", f"-{n}", "--pretty=format:%h|%s"])
    rows = []
    for line in out.splitlines():
        if "|" in line:
            h, s = line.split("|", 1)
            rows.append({"hash": h, "subject": s})
    return rows


def broken_refs() -> List[str]:
    """Find README/docs mentions of files that don't exist."""
    broken = []
    readme = ROOT / "README.md"
    if not readme.exists():
        return broken
    for m in re.finditer(r"`([\w./-]+\.py|[\w./-]+\.json|[\w./-]+\.yaml)`", readme.read_text(errors="replace")):
        ref = m.group(1)
        if ref.startswith("."):
            continue
        if not (ROOT / ref).exists():
            broken.append(ref)
    return broken


def run() -> Dict[str, Any]:
    health = {}
    try:
        sys.path.insert(0, str(ROOT))
        from api.health import collect_health
        health = collect_health()
    except Exception as e:
        health = {"error": str(e)[:120]}

    return {
        "agent": "scout",
        "modules": count_modules(),
        "tests": count_tests(),
        "health": health,
        "dirty": len(dirty_files()),
        "recent_commits": recent_commits(),
        "broken_refs": broken_refs(),
        "verdict": "stable" if not dirty_files() else "drifting",
    }
