#!/usr/bin/env python3
"""ETP-1 ceremony checklist — tracks phase completion (lab)."""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path
HERE = Path(__file__).resolve().parent
STATE = HERE / "etp_state.json"
PHASES = [
    {"phase": 0, "name": "announce", "requires": ["testament", "quorum"]},
    {"phase": 1, "name": "parallel_accept", "requires": ["dual_suite_runtime"]},
    {"phase": 2, "name": "identity_migration", "requires": ["dual_control", "migration_map"]},
    {"phase": 3, "name": "archive_seal", "requires": ["merkle_root_e_n", "manifest_e_n1"]},
    {"phase": 4, "name": "deprecate", "requires": ["grace_elapsed", "commit_testament"]},
]

def load() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"protocol": "ETP-1", "target": None, "completed": {}, "status": "idle"}

def save(st: dict) -> None:
    STATE.write_text(json.dumps(st, indent=2) + "\n")

def start(target: str) -> dict:
    st = {"protocol": "ETP-1", "target": target, "completed": {}, "status": "in_progress", "started": datetime.now(timezone.utc).isoformat()}
    if target in ("E_INF", "EINF", "E∞"):
        st["emergency"] = True
    save(st)
    return st

def complete(phase: int, note: str = "") -> dict:
    st = load()
    st.setdefault("completed", {})[str(phase)] = {"ts": datetime.now(timezone.utc).isoformat(), "note": note}
    done = {int(k) for k in st["completed"]}
    needed = {p["phase"] for p in PHASES}
    if st.get("emergency"):
        needed.add(5)
    if needed <= done:
        st["status"] = "committed"
        st["committed"] = datetime.now(timezone.utc).isoformat()
    save(st)
    return {"ok": True, "state": st}

def status() -> dict:
    st = load()
    done = {int(k) for k in st.get("completed", {})}
    pending = [p for p in PHASES if p["phase"] not in done]
    return {"state": st, "pending": pending, "ok": True}

def main() -> int:
    act = sys.argv[1] if len(sys.argv) > 1 else "status"
    if act == "start":
        print(json.dumps(start(sys.argv[2] if len(sys.argv) > 2 else "E2"), indent=2))
        return 0
    if act == "complete":
        print(json.dumps(complete(int(sys.argv[2]) if len(sys.argv) > 2 else 0, sys.argv[3] if len(sys.argv) > 3 else ""), indent=2))
        return 0
    if act == "status":
        print(json.dumps(status(), indent=2))
        return 0
    print(json.dumps({"ok": False, "err": "usage: start|complete|status"}))
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
