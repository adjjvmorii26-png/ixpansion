#!/usr/bin/env python3
"""PR Graft Advisor — hold | observe | act."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
def run_json(cmd, timeout=90):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        try: return json.loads(r.stdout or "{}")
        except json.JSONDecodeError: return {"ok": r.returncode == 0}
    except Exception as e:
        return {"ok": False, "err": str(e)}
def advise():
    smoke = run_json([sys.executable, str(REPO / "lab" / "smoke_lab.py")])
    helix = run_json([sys.executable, str(REPO / "lab" / "helix_bridge" / "probe.py")])
    null = run_json([sys.executable, str(REPO / "lab" / "null_orchard" / "map_absence.py")])
    ticket = run_json([sys.executable, str(REPO / "lab" / "ops" / "epoch_ticket.py"), "verify"])
    scores = [1.0 if smoke.get("ok") else 0.0, 1.0 if helix.get("ok") else 0.0]
    voids = null.get("voids") or []
    critical = [v for v in voids if v.get("name") in ("chronoforge", "stratum", "helix")]
    scores.append(0.0 if critical else 0.85)
    mode = ticket.get("mode", "hold")
    scores.append({"act": 1.0, "observe": 0.55, "hold": 0.2}.get(mode, 0.2))
    fused = sum(scores) / len(scores); uncertainty = 0.12
    low, high = fused - uncertainty, fused + uncertainty; thr = 0.72
    if high < thr: action, why = "hold", "below_threshold"
    elif low > thr: action, why = "act", "lab_graft_green"
    else: action, why = "observe", "band_crosses_threshold"
    out = {"ok": True, "protocol": "GRAFT-1", "ts": datetime.now(timezone.utc).isoformat(), "fused": round(fused, 4), "band": [round(low, 4), round(high, 4)], "threshold": thr, "action": action, "reason": why, "signals": {"smoke": smoke.get("ok"), "helix": helix.get("ok"), "critical_voids": critical, "ticket_mode": mode}, "note": "Advice only — does not merge."}
    dest = REPO / "lab" / "ops" / "graft_reports"; dest.mkdir(parents=True, exist_ok=True)
    path = dest / f"graft_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    path.write_text(json.dumps(out, indent=2) + "\n"); out["wrote"] = str(path)
    return out
def main():
    out = advise(); print(json.dumps(out, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
