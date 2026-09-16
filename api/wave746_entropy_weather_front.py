"""Wave 746 Entropy Weather Front — climate from vitals volatility."""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave746_entropy_weather_front.json"
DEFAULT = {"module": "wave746_entropy_weather_front", "wave": 746, "samples": [], "front": "calm"}


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


def _classify(samples: list) -> str:
    if len(samples) < 2:
        return "calm"
    vals = [float(s.get("v") or 0) for s in samples[-12:]]
    mean = sum(vals) / len(vals)
    var = sum((x - mean) ** 2 for x in vals) / len(vals)
    if var < 0.05: return "calm"
    if var < 0.25: return "breeze"
    if mean > 0 and vals[-1] < mean * 0.5: return "inversion"
    return "storm"


def coherence_vitals():
    st = _load()
    return {"wave": 746, "module": "wave746_entropy_weather_front", "ok": True,
            "front": st.get("front", "calm"), "samples": len(st.get("samples") or [])}


def resonates_with():
    return ["wave436_entropic_weather", "wave701_still_compound", "wave737_paradox_debt_ledger"]


def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    if action == "sample":
        v = float(req.get("v") or req.get("value") or 0)
        samples = st.setdefault("samples", [])
        samples.append({"v": v, "tag": str(req.get("tag") or "")[:32],
                        "ts": datetime.now(timezone.utc).isoformat()})
        st["samples"] = samples[-48:]
        st["front"] = _classify(st["samples"])
        _save(st)
        return {"status": "sampled", "front": st["front"], **coherence_vitals()}
    if action == "forecast":
        return {"status": "forecast", "front": st.get("front", "calm"), "hint": {
            "calm": "favor still_compound", "breeze": "normal routing",
            "storm": "raise paradox ceiling caution", "inversion": "prefer quarantine / compost",
        }.get(st.get("front", "calm")), **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "sample", "v": 0.4, "tag": "debt"}), indent=2))
