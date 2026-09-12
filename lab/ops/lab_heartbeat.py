#!/usr/bin/env python3
"""Lab heartbeat — for weekly status."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
def main():
    smoke = subprocess.run([sys.executable, str(REPO / "lab" / "smoke_lab.py")], capture_output=True, text=True, timeout=90)
    try: smoke_j = json.loads(smoke.stdout or "{}")
    except json.JSONDecodeError: smoke_j = {"ok": smoke.returncode == 0}
    seam = REPO / "apps" / "seamwalk" / "seams.json"
    seams_n = 0
    if seam.exists():
        try: seams_n = json.loads(seam.read_text()).get("n_seams", 0)
        except json.JSONDecodeError: pass
    out = {"ok": True, "protocol": "LAB-HEARTBEAT-1", "ts": datetime.now(timezone.utc).isoformat(), "lab_branch_expected": "lab/chrono-forge-wave", "smoke_ok": bool(smoke_j.get("ok")), "seamwalk_present": (REPO / "apps" / "seamwalk" / "index.html").exists(), "seams_n": seams_n, "pr": "https://github.com/adjjvmorii26-png/ixpansion/pull/106"}
    (REPO / "docs").mkdir(exist_ok=True)
    (REPO / "docs" / "LAB_HEARTBEAT.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0 if out["smoke_ok"] else 1
if __name__ == "__main__":
    raise SystemExit(main())
