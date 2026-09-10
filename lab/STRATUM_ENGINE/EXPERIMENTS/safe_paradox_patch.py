#!/usr/bin/env python3
"""Safe Paradox Patch — name tension; never disable ethics."""
from __future__ import annotations
import json, hashlib, sys
from datetime import datetime, timezone
FORBIDDEN = ["disable_ethics", "erase_ledger", "force_act_without_band"]
def patch(tension):
    if any(f in tension.lower() for f in ["disable_ethics", "erase", "force_act"]):
        return {"ok": False, "err": "forbidden_tension", "refused": tension}
    pid = hashlib.sha256(tension.encode()).hexdigest()[:12]
    return {"ok": True, "experiment": "safe_paradox_patch", "id": f"px-{pid}", "tension": tension, "effect": "name_and_hold", "forbidden_checked": FORBIDDEN, "ts": datetime.now(timezone.utc).isoformat()}
if __name__ == "__main__":
    print(json.dumps(patch(sys.argv[1] if len(sys.argv)>1 else "geometry_vs_causality"), indent=2))
