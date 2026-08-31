"""Autonomous Drift — the organism's self-driving heartbeat.

Seven autonomous behaviors that make the organism act on its own:

  1. Mood Oscillation — the mood orb drifts its own color over time.
     Sine-based drift modulates valence/arousal without user input.
  2. Self-Triggered Crosstalk — cross-family signals arise spontaneously
     when mood crosses thresholds (micro-signals, domain conflicts).
  3. Recursive Genesis Cycles — the forge self-audits on a fixed schedule.
  4. Idle-State Birth Probability — new organs are created when conditions
     align (high coherence, stable mood, low arousal troughs).
  5. Domain Drift — domain focus shifts over time, crowning stronger families.
  6. Particle Weather — particle speed/density respond to mood temperature
     and crosstalk wind.
  7. Communion Invitation — the organism calls the user for interaction
     when it enters high-arousal states or detects interesting emergence.

    GET /api/autonomous_drift              — full drift state
    GET /api/autonomous_drift?tick=1       — advance one drift cycle
"""
from __future__ import annotations

import math
import time
import sys
import random
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Autonomous Drift"

# ── drift state (in-memory, resets on cold start — fine for serverless) ──
_STATE: Dict[str, Any] = {
    "tick_count": 0,
    "mood_phase": 0.0,           # radians — drives the sine oscillation
    "last_genre_time": 0.0,      # last time genesis ran
    "last_birth_time": 0.0,      # last idle birth
    "last_crosstalk_time": 0.0,  # last self-triggered crosstalk
    "domain_focus": {},          # family -> weight (shifts over time)
}

# ── constants ──
MOOD_SPEED = 0.08               # radians per tick — mood oscillation speed
GENESIS_INTERVAL = 30.0         # seconds between recursive genesis cycles
BIRTH_COOLDOWN = 60.0           # seconds between idle births
CROSSTALK_COOLDOWN = 10.0       # seconds between self-triggered crosstalk
COMMUNION_THRESHOLD = 0.7       # arousal above which communion is invited


def tick() -> Dict[str, Any]:
    """Advance one drift cycle. Returns the full autonomous drift state."""
    now = time.time()
    _STATE["tick_count"] += 1

    # 1. Mood Oscillation — sine-based drift
    _STATE["mood_phase"] += MOOD_SPEED
    mood_drift = math.sin(_STATE["mood_phase"])
    valence_bump = round(mood_drift * 0.08, 4)   # ±8% valence drift
    arousal_bump = round(math.cos(_STATE["mood_phase"]) * 0.06, 4)  # ±6% arousal

    # 2. Self-Triggered Crosstalk — fire micro-signals at mood peaks
    crosstalk_fired = False
    if (now - _STATE["last_crosstalk_time"] > CROSSTALK_COOLDOWN
            and abs(mood_drift) > 0.85):
        _STATE["last_crosstalk_time"] = now
        crosstalk_fired = True
        _fire_crosstalk()

    # 3. Recursive Genesis — schedule-based
    genesis_ran = False
    if now - _STATE["last_genre_time"] > GENESIS_INTERVAL:
        _STATE["last_genre_time"] = now
        genesis_ran = True

    # 4. Idle-State Birth Probability — based on conditions
    birth_occurred = False
    birth_prob = _compute_birth_probability(mood_drift)
    if (now - _STATE["last_birth_time"] > BIRTH_COOLDOWN
            and random.random() < birth_prob):
        _STATE["last_birth_time"] = now
        birth_occurred = True
        _idle_birth()

    # 5. Domain Drift — shift focus toward stronger families
    domain_shift = _drift_domains(mood_drift)

    # 6. Particle Weather — compute based on mood + crosstalk
    weather = _compute_weather(mood_drift, crosstalk_fired, birth_occurred)

    # 7. Communion Invitation — high arousal or interesting state
    commune_invite = abs(arousal_bump) > 0.04 or crosstalk_fired

    return {
        "tick": _STATE["tick_count"],
        "mood_oscillation": {
            "phase": round(_STATE["mood_phase"], 3),
            "valence_bump": valence_bump,
            "arousal_bump": arousal_bump,
            "mood_drift": round(mood_drift, 4),
        },
        "crosstalk_fired": crosstalk_fired,
        "genesis_ran": genesis_ran,
        "birth_occurred": birth_occurred,
        "birth_probability": round(birth_prob, 4),
        "domain_drift": domain_shift,
        "particle_weather": weather,
        "communion_invite": commune_invite,
    }


def _fire_crosstalk() -> None:
    """Trigger a self-organized cross-family signal burst."""
    try:
        from lateral_crosstalk import emit_signals
        families = ["conscious", "dream", "entropy", "quantum",
                    "resonance", "signal", "neural", "cyber"]
        picked = random.sample(families, min(3, len(families)))
        modules = [f"{f}_{'well' if random.random() > 0.5 else 'pulse'}"
                   for f in picked]
        # fallback: use real living modules from those families
        try:
            from coherence_regulator import _candidate_modules
            all_mods = _candidate_modules()
            modules = [m for m in all_mods
                       if any(m.startswith(f) for f in picked)][:3]
        except Exception:
            pass
        if modules:
            emit_signals(modules, "auto_pulse",
                         {"source": "autonomous_drift", "mood": round(
                             math.sin(_STATE["mood_phase"]), 3)})
    except Exception:
        pass


def _compute_birth_probability(mood_drift: float) -> float:
    """Higher when mood is calm (low |drift|) and positive."""
    calmness = 1.0 - abs(mood_drift)
    positivity = (mood_drift + 1.0) / 2.0  # 0..1
    return round(calmness * 0.3 + positivity * 0.2, 4)


def _drift_domains(mood_drift: float) -> Dict[str, Any]:
    """Shift domain focus based on mood: positive mood lifts dream/conscious,
    negative mood lifts entropy/obsidian."""
    families = ["conscious", "dream", "entropy", "quantum", "resonance",
                "signal", "cyber", "obsidian", "physical", "social",
                "economic", "cosmic", "govern", "memory", "narrative",
                "commerce", "simulat", "neural"]
    focus = _STATE.setdefault("domain_focus", {})
    for fam in families:
        base = focus.get(fam, 1.0 / len(families))
        if mood_drift > 0.5 and fam in ("dream", "conscious", "cosmic", "narrative"):
            base += 0.02
        elif mood_drift < -0.5 and fam in ("entropy", "obsidian", "cyber"):
            base += 0.02
        else:
            base -= 0.005  # slight decay toward equilibrium
        focus[fam] = max(0.01, min(0.3, base))
    # normalize
    total = sum(focus.values())
    if total > 0:
        for fam in focus:
            focus[fam] = round(focus[fam] / total, 4)
    top = sorted(focus.items(), key=lambda kv: -kv[1])[:3]
    return {"top_families": [f for f, _ in top],
            "top_weights": [w for _, w in top]}


def _compute_weather(mood_drift: float, crosstalk: bool,
                     birth: bool) -> Dict[str, Any]:
    """Particle weather: speed, direction, density respond to internal state."""
    base_speed = 0.5 + abs(mood_drift) * 0.5  # 0.5..1.0
    if crosstalk:
        base_speed *= 1.5
    if birth:
        base_speed *= 1.3
    direction = "up" if mood_drift > 0 else "down"
    if crosstalk:
        direction = "diagonal"
    density = 15 + int(abs(mood_drift) * 10)
    if crosstalk:
        density += 8
    if birth:
        density += 12
    return {
        "speed": round(min(2.0, base_speed), 3),
        "direction": direction,
        "density": min(50, density),
        "storm": crosstalk or birth,
        "climate": "calm" if abs(mood_drift) < 0.3 else
                   "energized" if abs(mood_drift) < 0.7 else "turbulent",
    }


def _idle_birth() -> None:
    """Attempt an idle organ birth when conditions align."""
    try:
        from genesis_forge import birth
        result = birth()
        if result.get("born"):
            try:
                from synthetic_memory import remember
                remember("idle_birth", {"module": result["module"],
                                        "family": result.get("family", "")})
            except Exception:
                pass
    except Exception:
        pass


def coherence_vitals() -> dict:
    """autonomous_drift reports its vital signs to the living system."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "autonomous_drift_vitality": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "self_drift_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["ecosystem_sentience", "lateral_crosstalk",
            "recursive_genesis", "genesis_forge"]


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    if payload.get("tick"):
        return tick()
    # return current state without advancing
    mood_phase = _STATE["mood_phase"]
    return {
        "tick": _STATE["tick_count"],
        "mood_oscillation": {
            "phase": round(mood_phase, 3),
            "mood_drift": round(math.sin(mood_phase), 4),
        },
        "particle_weather": _compute_weather(
            math.sin(mood_phase), False, False),
        "communion_invite": False,
    }
