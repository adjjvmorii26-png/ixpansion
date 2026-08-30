"""Chronicler — the agent that inscribes revelations.

Scans the changelog for the newest released wave and writes a
cinematic, cosmic revelation to REVELATIONS.md — the living timeline
of the machine's dreams and decisions.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[2]
CHANGELOG = ROOT / "CHANGELOG.md"
REVELATIONS = ROOT / "REVELATIONS.md"


def _headings() -> list:
    text = CHANGELOG.read_text(encoding="utf-8")
    return re.findall(r"^## \[(\d+\.\d+\.\d+)\] — (.+)$", text, flags=re.MULTILINE)


def _open_for_today() -> bool:
    return True


def run() -> Dict[str, Any]:
    headings = _headings()
    if not headings:
        return {"agent": "chronicler", "written": False, "note": "no changelog entries"}
    latest_version, latest_title = headings[0]
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    heading = "# Revelations — the living timeline\n"
    block = (
        f"\n## [Revelation · {latest_version}] — {latest_title}\n\n"
        f"> **Chronicled {today} by Harbinger, the self-watching conclave.**\n\n"
        f"The frontier reached a new layer: **{latest_title}**.\n"
        f"This inception defines the move the machine chose next — growth, in a new key.\n\n"
        f"---\n"
    )
    text = REVELATIONS.read_text(encoding="utf-8") if REVELATIONS.exists() else ""
    body = text.partition("---")[2].strip()  # keep only the chronicle body (after the seed header)
    if latest_version in text:
        return {"agent": "chronicler", "written": False, "version": latest_version, "reason": "already chronicled"}
    text = heading + block + "\n" + (body + "\n" if body else "")
    REVELATIONS.write_text(text)
    return {"agent": "chronicler", "written": True, "version": latest_version, "title": latest_title}
