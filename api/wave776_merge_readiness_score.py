"""Wave 776 — merge_readiness_score.

Experimental: score a PR (or local snapshot) for merge readiness using
organism gates first, GHAS/external noise last. Dual-track: lab gates
are not ALEPH full CI.

Silence is the product surface.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave776_merge_readiness_score.json"
WAVE = 776
NAME = "merge_readiness_score"

DEFAULT = {"wave": WAVE, "name": NAME, "scores": 0, "status": "idle"}

# Weights: organism first, noise last.
WEIGHTS = {
    "lab_smoke": 0.28,
    "lab_graft": 0.22,
    "lab_gate": 0.22,
    "tests_green": 0.16,
    "ghas_alerts": 0.08,  # informational, never veto by itself
    "aleph_full_ci": 0.04,  # dual-track: must not block lab merge
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load() -> dict:
    if STATE_FILE.exists():
        try:
            raw = json.loads(STATE_FILE.read_text())
            if isinstance(raw, dict):
                return raw
        except Exception:
            pass
    return dict(DEFAULT)


def _save(st: dict) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    try:
        tmp = STATE_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(st, indent=2) + "\n")
        tmp.replace(STATE_FILE)
    except OSError:
        try:
            STATE_FILE.write_text(json.dumps(st, indent=2) + "\n")
        except OSError:
            pass


def _clamp(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def score_signals(signals: dict | None) -> dict:
    """signals values in [0,1]; ghas_alerts is inverted (more alerts = lower)."""
    s = signals or {}
    lab_smoke = _clamp(s.get("lab_smoke", 1.0))
    lab_graft = _clamp(s.get("lab_graft", 1.0))
    lab_gate = _clamp(s.get("lab_gate", 1.0))
    tests_green = _clamp(s.get("tests_green", 1.0))
    ghas_alerts = _clamp(s.get("ghas_alerts", 0.0))  # 0 = quiet
    aleph_full_ci = _clamp(s.get("aleph_full_ci", 0.5))

    parts = {
        "lab_smoke": lab_smoke * WEIGHTS["lab_smoke"],
        "lab_graft": lab_graft * WEIGHTS["lab_graft"],
        "lab_gate": lab_gate * WEIGHTS["lab_gate"],
        "tests_green": tests_green * WEIGHTS["tests_green"],
        "ghas_alerts": (1.0 - ghas_alerts) * WEIGHTS["ghas_alerts"],
        "aleph_full_ci": aleph_full_ci * WEIGHTS["aleph_full_ci"],
    }
    raw = sum(parts.values())
    organism = lab_smoke * lab_graft * lab_gate * tests_green
    # Organism veto: if any core lab gate is 0, readiness is 0 regardless of GHAS.
    ready = raw if organism > 0 else 0.0
    verdict = "mergeable" if ready >= 0.72 and organism > 0 else "hold"
    if organism == 0:
        verdict = "blocked_lab"
    return {
        "score": round(ready, 4),
        "parts": {k: round(v, 4) for k, v in parts.items()},
        "organism_product": round(organism, 4),
        "verdict": verdict,
        "policy": "organism_gates_gt_ghas_noise",
    }


def coherence_vitals() -> dict:
    st = _load()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave776_merge_readiness_score",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "scores": int(st.get("scores") or 0),
        "policy": "organism_gates_gt_ghas_noise",
        "resonance": round(min(1.0, 0.5 + int(st.get("scores") or 0) * 0.01), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave773_ci_sentinel_bridge",
        "wave775_constellation_affinity",
        "wave770_copilot_council_pulse",
        "lab.ops.copilots.helix",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {
            **coherence_vitals(),
            "weights": WEIGHTS,
            "audio": False,
            "surface": "silence",
        }

    if action == "score":
        result = score_signals(req.get("signals") or {})
        st["scores"] = int(st.get("scores") or 0) + 1
        st["status"] = result["verdict"]
        st["last_score"] = result["score"]
        st["last_ts"] = _now()
        st["last_ref"] = str(req.get("ref") or "local")
        _save(st)
        return {
            **coherence_vitals(),
            **result,
            "ref": st["last_ref"],
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("scores") or 0)
        last = st.get("last_score")
        cap = f"readiness scores {n}"
        if last is not None:
            cap += f" · last {last}"
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": cap,
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "score", "signals": {"lab_smoke": 1, "lab_graft": 1, "lab_gate": 1, "tests_green": 1, "ghas_alerts": 0.3}}), indent=2))
