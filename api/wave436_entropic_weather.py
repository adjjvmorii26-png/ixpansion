"""Wave 436 Entropic Weather — storms/fog/aurora drive organism behavior."""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave436_entropic_weather.json"
WEATHERS = ("clear", "fog", "storm", "aurora", "drought")
DEFAULT = {"module": "wave436_entropic_weather", "wave": 436, "sky": "clear", "entropy": 0.3, "ticks": 0}
def _load():
    if STATE_FILE.exists():
        try: return json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError: pass
    return dict(DEFAULT)
def _save(st):
    DATA.mkdir(parents=True, exist_ok=True); STATE_FILE.write_text(json.dumps(st, indent=2) + "\n")
def coherence_vitals():
    st = _load()
    return {"wave": 436, "module": "wave436_entropic_weather", "ok": True, "sky": st.get("sky"), "entropy": st.get("entropy")}
def resonates_with():
    return ["wave435_resonance_cartography", "wave431_homestead"]
def handler(req=None):
    req = req or {}; action = (req.get("action") or "status").lower(); st = _load()
    if action == "tick":
        seed = f"{st.get('ticks', 0)}:{st.get('sky')}:{datetime.now(timezone.utc).isoformat()}"
        h = hashlib.sha256(seed.encode()).digest()
        st["sky"] = WEATHERS[h[0] % len(WEATHERS)]; st["entropy"] = round(h[1] / 255.0, 3)
        st["ticks"] = int(st.get("ticks") or 0) + 1; st["ts"] = datetime.now(timezone.utc).isoformat(); _save(st)
        return {"status": "ticked", **st, **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}
