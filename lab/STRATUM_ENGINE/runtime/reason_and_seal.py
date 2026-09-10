#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone
SE = Path(__file__).resolve().parent.parent
def run():
    ethics_fail = len(sys.argv) > 1 and sys.argv[1] == "fail"
    r = subprocess.run([sys.executable, str(SE / "EMERGENT_LAYER" / "reasoning" / "reason_engine.py")] + (["fail"] if ethics_fail else []), capture_output=True, text=True)
    decision = json.loads(r.stdout or "{}")
    pk = json.loads(subprocess.run([sys.executable, str(SE / "PK_HEX" / "bind.py")], capture_output=True, text=True).stdout or "{}")
    audit = SE / "SUPERVISION_LAYER" / "audit_trail" / "audit.log"
    audit.parent.mkdir(parents=True, exist_ok=True)
    with audit.open("a") as f:
        f.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(), "type": "reason_and_seal", "action": decision.get("action"), "pk_bound": (pk.get("pk") or {}).get("bound")}) + "\n")
    return {"ok": decision.get("ok") and pk.get("ok"), "decision": decision, "pk": pk.get("pk"), "audited": True}
if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
