"""Wave 745 Mirror-World Delta — shadow twin state and diff."""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave745_mirror_world_delta.json"
DEFAULT = {"module": "wave745_mirror_world_delta", "wave": 745, "wake": {}, "mirror": {}}


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
    wake, mir = st.get("wake") or {}, st.get("mirror") or {}
    keys = set(wake) | set(mir)
    diverged = sum(1 for k in keys if wake.get(k) != mir.get(k))
    return {"wave": 745, "module": "wave745_mirror_world_delta", "ok": True,
            "keys": len(keys), "diverged": diverged}


def resonates_with():
    return ["wave709_rift_choir_twin_d28a", "wave738_oblivion_compost", "wave703_proof_delta"]


def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    wake = st.setdefault("wake", {})
    mir = st.setdefault("mirror", {})
    if action == "commit":
        key = str(req.get("key") or "")[:64]
        if not key: return {"status": "empty", **coherence_vitals()}
        wake[key] = req.get("value")
        st["wake"] = wake
        _save(st)
        return {"status": "committed", "key": key, **coherence_vitals()}
    if action == "mirror":
        key = str(req.get("key") or "")[:64]
        if not key: return {"status": "empty", **coherence_vitals()}
        mir[key] = req.get("value")
        st["mirror"] = mir
        _save(st)
        return {"status": "mirrored", "key": key, **coherence_vitals()}
    if action == "delta":
        keys = sorted(set(wake) | set(mir))
        diffs = [{"key": k, "wake": wake.get(k), "mirror": mir.get(k)}
                 for k in keys if wake.get(k) != mir.get(k)]
        return {"status": "delta", "diffs": diffs[:32], "n": len(diffs), **coherence_vitals()}
    if action == "collapse":
        side = str(req.get("side") or "wake")
        if side == "mirror":
            st["wake"] = dict(mir)
        else:
            st["mirror"] = dict(wake)
        st["collapsed"] = datetime.now(timezone.utc).isoformat()
        _save(st)
        return {"status": "collapsed", "side": side, **coherence_vitals()}
    if action == "status":
        return {"status": "active", **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
