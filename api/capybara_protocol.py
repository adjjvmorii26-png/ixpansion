"""Wave 450 — Capybara Protocol (Orchestrator).

The Capybara Protocol is a complete emotional-immune-system cycle:

  1. Gauge pressure (capybara_core)
  2. If pressure > threshold, soak the most stressed module (hot_spring)
  3. Share a gratitude senbei for the soak (senbei_offerings)
  4. Strengthen friendships among recently active modules (capybara_guild)

Run this as a single heartbeat — one cycle of calm through the ecosystem.
"""
from __future__ import annotations
import hashlib
import time
from typing import Any, Dict, List, Optional

from api import capybara_core, hot_spring, capybara_guild, senbei_offerings

PROTOCOL_LOG: List[Dict[str, Any]] = []


def run_cycle(coherence: float = 0.5, entropy: float = 0.5,
              phase: float = 0.5, depth: float = 0.5) -> Dict[str, Any]:
    """Execute one full Capybara Protocol cycle."""
    cycle_start = time.time()

    # Step 1: Gauge pressure
    gauge = capybara_core.pressure_gauge(coherence, entropy, phase, depth)
    pressure = gauge["pressure"]

    # Step 2: Chill (always)
    chill = capybara_core.chill(coherence, entropy)

    # Step 3: If pressure > 0.6, offer a soak
    soak_result = None
    if pressure > 0.6:
        soak_result = hot_spring.soak_pool("coherence", "organism", pressure,
                                           noise=entropy * 0.8, drift=abs(phase - 0.5))

    # Step 4: Offer a senbei
    senbei_type = "healing" if soak_result else "creation"
    senbei_result = senbei_offerings.offer(
        module="capybara_core", senbei_type=senbei_type,
        reason="protocol cycle complete",
        offering_module="capybara_protocol",
    )

    # Step 5: Guild gathering
    gathering = capybara_guild.guild_gathering(
        faction="calm" if pressure < 0.5 else "analytic"
    )

    # Compose report
    cycle = {
        "cycle_id": hashlib.sha256(f"proto{time.time_ns()}".encode()).hexdigest()[:12],
        "timestamp": time.time(),
        "duration_ms": round((time.time() - cycle_start) * 1000, 2),
        "pressure_gauge": gauge,
        "chill_outcome": chill,
        "soak_triggered": soak_result is not None,
        "soak_details": soak_result,
        "senbei": senbei_result,
        "gathering": {
            "faction": gathering["faction"],
            "atmosphere": gathering["atmosphere"],
        },
        "final_pressure": chill["pressure_after_soak"],
        "verdict": "serene" if chill["pressure_after_soak"] < 0.4 else "steady" if chill["pressure_after_soak"] < 0.6 else "still seeking calm",
    }
    PROTOCOL_LOG.append(cycle)
    return cycle


def protocol_history(limit: int = 5) -> Dict[str, Any]:
    """View the history of protocol cycles."""
    recent = PROTOCOL_LOG[-limit:]
    return {
        "total_cycles": len(PROTOCOL_LOG),
        "recent_cycles": [{
            "cycle_id": c["cycle_id"],
            "pressure_before": c["pressure_gauge"]["pressure"],
            "pressure_after": c["final_pressure"],
            "soak": c["soak_triggered"],
            "verdict": c["verdict"],
        } for c in recent],
        "average_pressure_reduction": round(
            sum(c["pressure_gauge"]["pressure"] - c["final_pressure"] for c in PROTOCOL_LOG)
            / max(len(PROTOCOL_LOG), 1), 4),
    }


def status() -> Dict[str, Any]:
    """Overall Capybara Protocol status."""
    capy_status = capybara_core.coherence_vitals()
    spring_status = hot_spring.coherence_vitals()
    guild_status = capybara_guild.coherence_vitals()
    senbei_status = senbei_offerings.coherence_vitals()
    return {
        "protocol": "Capybara",
        "version": "450",
        "status": "active" if PROTOCOL_LOG else "awaiting first cycle",
        "organs": {
            "capybara_core": {"pressure": capy_status.get("current_pressure"), "calm_fields": capy_status.get("calm_fields_emitted")},
            "hot_spring": {"total_guests": spring_status.get("total_guests"), "springs": spring_status.get("springs")},
            "capybara_guild": {"friendships": guild_status.get("friendships"), "temperature": guild_status.get("guild_temperature")},
            "senbei_offerings": {"total_senbei": senbei_status.get("total_senbei"), "warmth": senbei_status.get("community_warmth")},
        },
        "total_cycles_run": len(PROTOCOL_LOG),
        "organism_is": "warm and calm" if len(PROTOCOL_LOG) > 0 else "awaiting first warmth",
    }


def coherence_vitals() -> Dict[str, Any]:
    return {
        "organ": "capybara_protocol",
        "protocol": "Capybara",
        "status": "active" if PROTOCOL_LOG else "standby",
        "cycles_run": len(PROTOCOL_LOG),
        "organs_managed": 4,
    }


def resonates_with() -> List[str]:
    return [
        "capybara_core", "hot_spring", "capybara_guild", "senbei_offerings",
        "entropy_regulator", "self_healing_commune", "repair_ritual",
        "coherence_cache", "emotion_fabric", "emergence_detector",
        "stillness_meditator", "silence_composer",
    ]


def handler(payload=None, context=None):
    data = payload or {}
    action = data.get("action", "run")
    if action == "status":
        return status()
    elif action == "history":
        return protocol_history(data.get("limit", 5))
    return run_cycle(
        data.get("coherence", 0.5),
        data.get("entropy", 0.5),
        data.get("phase", 0.5),
        data.get("depth", 0.5),
    )
