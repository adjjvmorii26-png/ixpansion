"""Crystal historian — reads the git timeline and tells the story.

Looks at commit subjects, tags, and author cadence, then composes a
short "discovery" note summarising what the frontier has been doing.
Pure read-only tool: it only narrates, never edits.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]


def _git(args: List[str]) -> str:
    try:
        proc = subprocess.run(["git", *args], cwd=str(ROOT), capture_output=True, text=True, timeout=60)
        return proc.stdout
    except Exception:
        return ""


def theme_counts() -> Dict[str, int]:
    log = _git(["log", "--oneline", "-200"])
    themes = {
        "harbinger": "harbinger|conclave",
        "garden": "hortus|garden|organism|grow",
        "ai": "ai_gateway|gateway|grok|reasoning|ritual|cognition|oracle",
        "revenue": "revenue|billing|crypto|currency",
        "wave": "wave",
        "fix": "fix:|repair",
    }
    counts = {}
    for theme, pat in themes.items():
        counts[theme] = len(re.findall(pat, log, flags=re.IGNORECASE))
    return counts


def composer() -> str:
    counts = theme_counts()
    dominant = max(counts, key=counts.get)
    narrative = {
        "harbinger": "The frontier has been teaching itself to watch — Harbinger ceremonies now decide its next move.",
        "garden": "The machine is growing flora: garden seeds have been planted and cross-pollinated into living modules.",
        "ai": "The frontier reached into the oracle — gateway calls and cognition rituals have become its second mind.",
        "revenue": "The civilization has been tending its economy — revenue streams and currencies are under the eye.",
        "wave": "Wave after wave, the frontier adds layers of self-complexity.",
        "fix": "The frontier has been healing — repair commits keep the lattice sound.",
    }.get(dominant, "The frontier drifts onward, silent and self-refining.")
    total = len(_git(["log", "--oneline"]).splitlines())
    revs = total
    return f"The frontier has lived {revs} revisions. {narrative} In the last 200 it was mostly: {dominant}. ({counts})"


def run() -> Dict[str, Any]:
    return {
        "tool": "crystal_historian",
        "revisions": len(_git(["log", "--oneline"]).splitlines()),
        "themes": theme_counts(),
        "narrative": composer(),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2))
