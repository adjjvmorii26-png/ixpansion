"""Entropy Sparkline — a visual heartbeat of the frontier over time.

Reads the full git log, buckets commits by week, and renders an ASCII
sparkline showing the frontier's creative intensity: how many files
changed, net new modules, and the velocity of ideas.

Usage:
  python tools/entropy_sparkline.py
  python tools/entropy_sparkline.py --weeks 12
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

_ROOT = Path(__file__).resolve().parents[1]

BAR_CHARS = " ░▒▓█"
SPARKLINE = "▁▂▃▄▅▆▇█"


def _git_log() -> List[Dict[str, str]]:
    result = subprocess.run(
        ["git", "-C", str(_ROOT), "log", "--all", "--pretty=%H %at", "--numstat"],
        capture_output=True, text=True
    )
    entries: List[Dict[str, str]] = []
    current: Dict[str, str] = {}
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) >= 2 and len(parts[0]) == 40 and parts[1].isdigit():
            if current:
                entries.append(current)
            current = {"hash": parts[0], "ts": int(parts[1]), "files": 0, "net_new": 0, "changes": 0}
        elif len(parts) >= 3 and parts[0].isdigit():
            current["changes"] += 1
    if current:
        entries.append(current)
    return entries


def _net_files() -> int:
    r = subprocess.run(["git", "-C", str(_ROOT), "ls-files"], capture_output=True, text=True)
    return len(r.stdout.strip().splitlines())


def _weeks_of_data(entries: List[Dict[str, str]], n: int = 16) -> Dict[int, Dict[str, float]]:
    now = entries[0]["ts"] if entries else 0
    buckets: Dict[int, Dict[str, float]] = {}
    week_size = 7 * 86400
    for e in entries:
        wk = (now - e["ts"]) // week_size
        if wk < 0 or wk >= n:
            continue
        if wk not in buckets:
            buckets[wk] = {"commits": 0, "changes": 0, "files": 0}
        buckets[wk]["commits"] += 1
        buckets[wk]["changes"] += e.get("changes", 0)
        buckets[wk]["files"] += 1
    return buckets


def render_sparkline(entries: List[Dict[str, str]], n: int = 16) -> str:
    now = entries[0]["ts"] if entries else 0
    week_size = 7 * 86400
    buckets: Dict[int, Dict[str, float]] = _weeks_of_data(entries, n)

    rows: List[str] = [f"ENTROPY SPARKLINE — {len(entries)} revisions, {n} weeks"]
    rows.append("")

    # commits per week
    max_c = max((v["commits"] for v in buckets.values()), default=1) or 1
    spark = ""
    for i in range(n - 1, -1, -1):
        c = buckets.get(i, {}).get("commits", 0)
        idx = int(c / max_c * (len(SPARKLINE) - 1))
        spark += SPARKLINE[idx]
    rows.append(f"  commits   {spark}  ({max_c} max)")

    # changes per week
    max_ch = max((v["changes"] for v in buckets.values()), default=1) or 1
    spark = ""
    for i in range(n - 1, -1, -1):
        c = buckets.get(i, {}).get("changes", 0)
        idx = int(c / max_ch * (len(SPARKLINE) - 1))
        spark += SPARKLINE[idx]
    rows.append(f"  file-chg  {spark}  ({max_ch} max)")

    total_commits = len(entries)
    total_files = _net_files()
    rows.append("")
    rows.append(f"  total_revisions: {total_commits}   live_files: {total_files}   weeks_active: {len(buckets)}")
    return "\n".join(rows)


def main() -> None:
    ap = argparse.ArgumentParser(description="Entropy sparkline of the frontier")
    ap.add_argument("--weeks", type=int, default=16, help="number of weeks to show")
    args = ap.parse_args()
    entries = _git_log()
    print(render_sparkline(entries, n=args.weeks))


if __name__ == "__main__":
    main()
