#!/usr/bin/env python3
"""Boot the organism base (ethics-first portals)."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PORTALS = [
    ("polygenesis", ROOT / "lab" / "polygenesis" / "pg_portal.py"),
    ("chronoweave", ROOT / "lab" / "chronoweave" / "cw_portal.py"),
    ("paradox_forge", ROOT / "lab" / "paradox_forge" / "pf_portal.py"),
]

def run(name: str, script: Path) -> dict:
    if not script.exists():
        return {"name": name, "ok": False, "err": "missing"}
    r = subprocess.run([sys.executable, str(script), "boot"], capture_output=True, text=True)
    ok = r.returncode == 0
    return {"name": name, "ok": ok, "out": (r.stdout or "")[:200]}

def main() -> int:
    results = [run(n, p) for n, p in PORTALS]
    pinned = ROOT / "lab" / "run_pinned.py"
    if pinned.exists():
        r = subprocess.run([sys.executable, str(pinned)], capture_output=True, text=True, timeout=120)
        results.append({"name": "pinned", "ok": r.returncode == 0})
    report = {"base": "organism", "results": results, "ok": all(x.get("ok") for x in results)}
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
