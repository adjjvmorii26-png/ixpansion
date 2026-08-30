"""Archivist — the agent that writes the official changelog entry.

When the conclave executes a wave, the archivist appends a clean,
versioned entry to CHANGELOG.md and returns the version it minted.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path(__file__).resolve().parents[2]
CHANGELOG = ROOT / "CHANGELOG.md"


def _latest_version() -> str:
    if not CHANGELOG.exists():
        return "3.0.0"
    text = CHANGELOG.read_text(encoding="utf-8")
    m = re.search(r"^## \[(\d+\.\d+\.\d+)\]", text, flags=re.MULTILINE)
    return m.group(1) if m else "3.0.0"


def _next_patch(version: str) -> str:
    major, minor, patch = version.split(".")
    return f"{major}.{minor}.{int(patch) + 1}"


def mint(version: str) -> str:
    """Increment the patch version for a new archived wave."""
    return _next_patch(version)


def append(title: str, version: Optional[str] = None, body: str = "") -> Dict[str, Any]:
    if not version:
        version = mint(_latest_version())
    header = "# Changelog\n\n"
    entry = f"## [{version}] — {title}\n\n{body.strip()}\n\n"
    text = CHANGELOG.read_text(encoding="utf-8")
    if not text.startswith(header):
        text = header + text
    if f"## [{version}]" in text:
        return {"version": version, "written": False, "reason": "exists"}
    text = header + entry + text[len(header):]
    CHANGELOG.write_text(text)
    return {"version": version, "written": True}


def run(title: str, body: str = "") -> Dict[str, Any]:
    version = mint(_latest_version())
    return {"agent": "archivist", "version": version, "entry": append(title, version, body)}
