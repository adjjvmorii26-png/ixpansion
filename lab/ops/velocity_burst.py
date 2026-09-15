#!/usr/bin/env python3
"""velocity_burst.py — Measure the organism's development velocity in a single burst.

Outputs:
  - commit cadence (commits/day over recent window)
  - new modules added recently
  - test suite growth
  - wave progression rate
  - overall velocity score (0-100)
"""
import subprocess, json, time, os
from pathlib import Path
from collections import Counter

REPO = Path(__file__).resolve().parents[2]
TESTS = REPO / "tests"
API  = REPO / "api"
DATA = REPO / "data"
WINDOW_DAYS = 7

def _run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=REPO)
    return r.stdout.strip()

def _git_commits_since(days):
    since = f"{days} days ago"
    raw = _run(f'git log --oneline --since="{since}" --format="%H %ai" main 2>/dev/null')
    if not raw:
        return []
    out = []
    for line in raw.splitlines():
        parts = line.split(" ", 1)
        if len(parts) == 2:
            out.append({"hash": parts[0][:8], "date": parts[1][:10]})
    return out

def _count_waves():
    raw = _run("ls api/wave*.py 2>/dev/null | wc -l")
    return int(raw) if raw.isdigit() else 0

def _count_tests():
    raw = _run("find tests -name 'test_*.py' 2>/dev/null | wc -l")
    return int(raw) if raw.isdigit() else 0

def _count_modules():
    raw = _run("ls api/*.py 2>/dev/null | wc -l")
    return int(raw) if raw.isdigit() else 0

def _latest_wave():
    import re
    nums = []
    for f in API.glob("wave*.py"):
        m = re.match(r"wave(\d+)", f.name)
        if m:
            nums.append(int(m.group(1)))
    return max(nums) if nums else 0

def _recent_waves_since(days):
    since = time.time() - days * 86400
    count = 0
    for f in API.glob("wave*.py"):
        if f.stat().st_mtime >= since:
            count += 1
    return count

def _recent_tests_since(days):
    since = time.time() - days * 86400
    return sum(1 for f in TESTS.glob("test_*.py") if f.stat().st_mtime >= since)

def _data_churn():
    modified = 0
    for f in DATA.glob("*.json"):
        if f.stat().st_mtime >= time.time() - 86400:
            modified += 1
    return modified

def velocity_score(commits, new_waves, new_tests, total_modules, total_waves):
    c = min(commits / 30, 1.0) * 30
    w = min(new_waves / 4, 1.0) * 30
    t = min(new_tests / 10, 1.0) * 20
    m = min(total_modules / 700, 1.0) * 10
    v = min(total_waves / 670, 1.0) * 10
    return round(c + w + t + m + v, 1)

def burst():
    commits = _git_commits_since(WINDOW_DAYS)
    today_commits = _git_commits_since(1)
    total_waves = _count_waves()
    total_tests = _count_tests()
    total_modules = _count_modules()
    latest_wave = _latest_wave()
    new_waves = _recent_waves_since(WINDOW_DAYS)
    new_tests = _recent_tests_since(WINDOW_DAYS)
    data_today = _data_churn()
    score = velocity_score(len(today_commits), new_waves, new_tests, total_modules, total_waves)

    print("=" * 58)
    print("  🔥  V E L O C I T Y   B U R S T")
    print("=" * 58)
    print(f"  Window          : last {WINDOW_DAYS} days")
    print(f"  Commits (7d)    : {len(commits)}")
    print(f"  Commits (today) : {len(today_commits)}")
    print(f"  New waves (7d)  : {new_waves}")
    print(f"  New tests (7d)  : {new_tests}")
    print(f"  Data churn (24h): {data_today} files touched")
    print("-" * 58)
    print(f"  Total waves     : {total_waves}  (latest: {latest_wave})")
    print(f"  Total modules   : {total_modules}")
    print(f"  Total test files: {total_tests}")
    print("-" * 58)
    bar = "█" * int(score / 2) + "░" * (50 - int(score / 2))
    print(f"  Velocity Score  : {score}/100")
    print(f"  [{bar}]")
    print("=" * 58)

    if commits:
        by_day = Counter(c["date"] for c in commits)
        print("\n  📅 Commits by day:")
        for d, n in sorted(by_day.items()):
            print(f"    {d}  {'█' * n}  {n}")
    print()
    return {"score": score, "commits_7d": len(commits), "new_waves": new_waves, "new_tests": new_tests}

if __name__ == "__main__":
    burst()
