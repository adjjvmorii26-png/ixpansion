"""Wave 742 Actuator Bridge — typed effectors only (dry-run default)."""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
ROOT = Path(__file__).parent.parent
OUT = ROOT / "content_output" / "actuators"
STATE_FILE = DATA / "wave742_actuator_bridge.json"
DEFAULT = {"module": "wave742_actuator_bridge", "wave": 742, "armed": False, "gas": 100, "log": []}


def _load():
    if STATE_FILE.exists():
        try: return json.loads(STATE_FILE.read_text())
        except Exception: pass
    return dict(DEFAULT)


def _save(st):
    DATA.mkdir(parents=True, exist_ok=True)
    try:
        tmp = STATE_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(st, indent=2) + "\n")
        tmp.replace(STATE_FILE)
    except OSError:
        try: STATE_FILE.write_text(json.dumps(st, indent=2) + "\n")
        except OSError: pass


def coherence_vitals():
    st = _load()
    return {"wave": 742, "module": "wave742_actuator_bridge", "ok": True,
            "armed": bool(st.get("armed")), "gas": st.get("gas", 0), "actions": len(st.get("log") or [])}


def resonates_with():
    return ["wave739_receipt_notary", "wave736_silent_broadcast_lattice", "wave737_paradox_debt_ledger"]


def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    if action == "arm":
        st["armed"] = True
        _save(st)
        return {"status": "armed", **coherence_vitals()}
    if action == "disarm":
        st["armed"] = False
        _save(st)
        return {"status": "disarmed", **coherence_vitals()}
    if action == "act":
        effector = str(req.get("effector") or "log")
        payload = req.get("payload") or {}
        cost = int(req.get("gas") or 5)
        gas = int(st.get("gas") or 0)
        if cost > gas:
            return {"status": "gas_exhausted", **coherence_vitals()}
        dry = not st.get("armed") or effector == "log" or bool(req.get("dry_run", True))
        result = {"effector": effector, "dry_run": dry, "payload": payload}
        if effector == "caption_file" and not dry:
            OUT.mkdir(parents=True, exist_ok=True)
            path = OUT / f"act_{int(datetime.now(timezone.utc).timestamp())}.json"
            path.write_text(json.dumps({"payload": payload, "ts": datetime.now(timezone.utc).isoformat()}, indent=2) + "\n")
            result["path"] = str(path.relative_to(ROOT))
        elif effector == "webhook_stub":
            result["note"] = "stub only — no network in lab default"
        st["gas"] = gas - cost
        log = st.setdefault("log", [])
        log.append({**result, "ts": datetime.now(timezone.utc).isoformat()})
        st["log"] = log[-48:]
        _save(st)
        return {"status": "acted", "result": result, **coherence_vitals()}
    if action == "refuel":
        st["gas"] = min(500, int(st.get("gas") or 0) + int(req.get("amount") or 50))
        _save(st)
        return {"status": "refueled", **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "act", "effector": "log", "payload": {"hello": True}}), indent=2))
