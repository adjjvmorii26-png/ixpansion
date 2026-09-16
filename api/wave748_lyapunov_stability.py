"""Wave 748 Lyapunov Stability Probe — finite-time divergence of vitals trajectories."""
from __future__ import annotations
import json, math
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave748_lyapunov_stability.json"
DEFAULT = {"module": "wave748_lyapunov_stability", "wave": 748, "series": [], "lambda_est": 0.0}


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


def estimate_lambda(series: list) -> float:
    if len(series) < 4: return 0.0
    vals = [float(x.get("v") or 0) for x in series[-16:]]
    deltas = [abs(vals[i + 1] - vals[i]) + 1e-9 for i in range(len(vals) - 1)]
    mid = len(deltas) // 2
    early = sum(deltas[:mid]) / max(mid, 1)
    late = sum(deltas[mid:]) / max(len(deltas) - mid, 1)
    return round(math.log((late + 1e-9) / (early + 1e-9)), 4)


def coherence_vitals():
    st = _load()
    return {"wave": 748, "module": "wave748_lyapunov_stability", "ok": True,
            "lambda_est": st.get("lambda_est", 0), "n": len(st.get("series") or []),
            "stable": float(st.get("lambda_est") or 0) < 0.1}


def resonates_with():
    return ["wave746_entropy_weather_front", "wave693_jerk_sensor", "wave744_phase_lock_clock"]


def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    if action == "observe":
        series = st.setdefault("series", [])
        series.append({"v": float(req.get("v") or req.get("value") or 0),
                       "ts": datetime.now(timezone.utc).isoformat()})
        st["series"] = series[-64:]
        st["lambda_est"] = estimate_lambda(st["series"])
        _save(st)
        return {"status": "observed", "lambda_est": st["lambda_est"], **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}


if __name__ == "__main__":
    for v in [0.1, 0.12, 0.11, 0.5, 0.9, 1.2]:
        handler({"action": "observe", "v": v})
    print(json.dumps(handler({"action": "status"}), indent=2))
