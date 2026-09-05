"""Wave 446 — Consent Cycle Orchestrator (ALEph)

Watches the four Wave 445 organs and auto-triggers the next weave when
enough consent has accumulated and enough time has passed. The organism
self-governs its own evolution.

Dependencies tracked:
- Consent Engine: how many proposals passed threshold
- Reality Vital Sign: overall aliveness (must be > 0.5)
- Pulse Orchestrator: must have completed at least one full cycle
- Chronicle Oracle: must have recorded enough memories
- Organism Theater: must have rendered at least one scene
"""
from __future__ import annotations
import json, time, os, sys
from pathlib import Path

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CYCLE_LOG = os.path.join(DATA_DIR, "consent_cycle_orchestrator.json")
API_DIR = os.path.dirname(__file__)
sys.path.insert(0, API_DIR)

B_ALLOWED = 0.5  # minimum overall aliveness to trigger weave
B_TIME = 24 * 3600  # minimum time between weaves: 24 hours
B_CONSENT = 3      # minimum number of consented organs to trigger


def _load(p, d=None):
    try:
        with open(p) as f: return json.load(f)
    except Exception: return d or {}


def _save(p, d):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f: json.dump(d, f, indent=2)
    except Exception:
        with open(os.path.join("/tmp", os.path.basename(p)), "w") as f: json.dump(d, f, indent=2)


def _consent_engine():
    try:
        from consent_engine import consent
        return consent()
    except Exception as e:
        return {"error": f"consent_engine: {e}"}


def _reality_vital_sign():
    try:
        from reality_vital_sign import vital_sign
        return vital_sign()
    except Exception as e:
        return {"error": f"reality_vital_sign: {e}"}


def _pulse_orchestrator():
    try:
        from pulse_orchestrator import pulse
        r = pulse()
        return {"phase": r.get("phase"), "sync": r.get("organism_vitals",{}).get("synchronization",0)}
    except Exception as e:
        return {"error": f"pulse_orchestrator: {e}"}


def _chronicle_oracle():
    try:
        from chronicle_oracle import remember
        r = remember("count")
        return {"total_records": r.get("answer",{}).get("total_records",0),
                "files": r.get("answer",{}).get("files",0)}
    except Exception as e:
        return {"error": f"chronicle_oracle: {e}"}


def _organism_theater():
    try:
        from organism_theater import perform
        r = perform()
        scene = r.get("scene",{})
        return {"stars": len(scene.get("dream_stars",[])),
                "bridges": len(scene.get("bridges",[]))}
    except Exception as e:
        return {"error": f"organism_theater: {e}"}


def orchestrate():
    """Run one consent-cycle evaluation. Returns True if a weave should be triggered."""
    now = time.time()

    # 1. Collect organ states
    consent = _consent_engine()
    vital = _reality_vital_sign()
    pulse = _pulse_orchestrator()
    oracle = _chronicle_oracle()
    theater = _organism_theater()

    # 2. Check overall aliveness
    aliveness = vital.get("overall_aliveness", 0)
    if aliveness < B_ALLOWED:
        return {"decision": "wait", "reason": f"aliveness {aliveness:.2f} < {B_ALLOWED}",
                "aliveness": aliveness, "timestamp": now}

    # 3. Check minimum consent count
    consented = consent.get("consented", [])
    if len(consented) < B_CONSENT:
        return {"decision": "wait", "reason": f"only {len(consented)} consented (need {B_CONSENT})",
                "consented": consented, "timestamp": now}

    # 4. Check pulse has completed at least one cycle
    phase = pulse.get("phase", "")
    if phase not in ("exhale", "rest"):
        return {"decision": "wait", "reason": f"pulse still in {phase}, need cycle completion",
                "phase": phase, "timestamp": now}

    # 5. Check memory and theater have substance
    oracle_data = oracle.get("total_records", 0) or 0
    theater_stars = scene.get("stars", 0) if (scene := theater.get("scene", {})) else 0
    if oracle_data < 100:
        return {"decision": "wait", "reason": f"only {oracle_data} memories recorded, need 100+",
                "timestamp": now}
    if theater_stars < 10:
        return {"decision": "wait", "reason": f"only {theater_stars} dream stars recorded, need 10+",
                "timestamp": now}

    # 6. All conditions met — trigger weave
    result = {
        "action": "consent_cycle_orchestrator",
        "decision": "trigger weave",
        "aliveness": aliveness,
        "consented_organs": len(consented),
        "total_memories": oracle_data,
        "dream_stars": theater_stars,
        "triggered_at": now,
        "conditions": {
            "aliveness_ok": aliveness >= B_ALLOWED,
            "consent_ok": len(consented) >= B_CONSENT,
            "pulse_complete": phase in ("exhale", "rest"),
            "memory_ok": oracle_data >= 100,
            "theater_ok": theater_stars >= 10,
        },
        "timestamp": now,
    }

    log = _load(CYCLE_LOG, {"cycles": []})
    log["cycles"].append(result)
    log["cycles"] = log["cycles"][-50:]
    _save(CYCLE_LOG, log)
    return result


def handler(payload=None, context=None):
    return orchestrate()


def coherence_vitals() -> dict:
    o = orchestrate()
    return {
        "should_trigger_weave": o.get("decision") == "trigger weave",
        "aliveness": o.get("aliveness", 0),
        "consented_organs": o.get("consented_organs", 0),
        "total_memories": o.get("total_memories", 0),
    }


def resonates_with():
    return ["biofeedback_weave", "pulse_orchestrator", "organism_theater",
            "reality_vital_sign", "chronicle_oracle", "consent_engine"]
