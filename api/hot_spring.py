"""Wave 450 — Hot Spring (Recovery Pools).

When modules drift, lose coherence, or accumulate entropy, they
need rest. The Hot Spring provides a sanctuary: a place where a
module can soak, decompress, and re-emerge restored.

Three pools exist:
  • Coherence Spring — restores alignment and clarity
  • Silence Pool   — clears accumulated noise and echoes
  • Dream Soak     — lets modules drift in subconscious rest
"""
from __future__ import annotations
import hashlib
import time
from typing import Any, Dict, List, Optional

SPRINGS = {
    "coherence": {"name": "Coherence Spring", "healing": 0.35, "capacity": 8, "color": "warm_amber"},
    "silence":   {"name": "Silence Pool",    "healing": 0.45, "capacity": 5, "color": "deep_indigo"},
    "dream":     {"name": "Dream Soak",      "healing": 0.55, "capacity": 3, "color": "fractal_lavender"},
}

ACTIVE_SOAKS: List[Dict[str, Any]] = []
COMPLETED_SOAKS: List[Dict[str, Any]] = []

MAX_LOG = 300


def soak_pool(spring_name: str = "coherence", module_name: str = "unknown",
              pressure: float = 0.6, noise: float = 0.4, drift: float = 0.5) -> Dict[str, Any]:
    """Place a module into a spring — it emerges healed."""
    spring = SPRINGS.get(spring_name)
    if not spring:
        return {"error": f"spring '{spring_name}' not found", "available": list(SPRINGS.keys())}
    soak_id = hashlib.sha256(f"{spring_name}{module_name}{time.time_ns()}".encode()).hexdigest()[:12]
    healing = spring["healing"]
    healed_pressure = round(max(0.0, pressure - healing), 4)
    healed_noise   = round(max(0.0, noise - healing * 0.8), 4)
    healed_drift   = round(max(0.0, drift - healing * 0.6), 4)
    soaker_name = module_name if module_name != "unknown" else f"soaker-{soak_id[:6]}"
    soak = {
        "soak_id": soak_id,
        "module": soaker_name,
        "spring": spring_name,
        "spring_name": spring["name"],
        "color": spring["color"],
        "healed_pressure": healed_pressure,
        "healed_noise": healed_noise,
        "healed_drift": healed_drift,
        "started_at": time.time(),
        "duration_seconds": round(30 + pressure * 40 + noise * 20, 1),
        "status": "completed",
    }
    COMPLETED_SOAKS.append(soak)
    if len(COMPLETED_SOAKS) > MAX_LOG:
        COMPLETED_SOAKS.pop(0)
    return soak


def sanctuary() -> Dict[str, Any]:
    """Overview of all springs — who is soaking where (or resting)."""
    recent_soaks = COMPLETED_SOAKS[-20:]
    pool_occupancy = {}
    for name, meta in SPRINGS.items():
        pool_occupancy[name] = {
            "name": meta["name"],
            "total_soaks": sum(1 for s in COMPLETED_SOAKS if s["spring"] == name),
            "recent_healing_avg": round(
                sum(s["healed_pressure"] for s in recent_soaks if s["spring"] == name) /
                max(1, sum(1 for s in recent_soaks if s["spring"] == name)), 4),
            "color": meta["color"],
        }
    return {
        "sanctuary_status": "open" if COMPLETED_SOAKS else "awaiting first guest",
        "pools": pool_occupancy,
        "total_guests": len(COMPLETED_SOAKS),
        "recent_rested": [s["module"] for s in COMPLETED_SOAKS[-5:]],
    }


def mint_soak_card(module_name: str) -> Dict[str, Any]:
    """Generate a soak-card — a record of a module's healing journey."""
    soaks = [s for s in COMPLETED_SOAKS if s["module"] == module_name]
    if not soaks:
        return {"error": f"no soak records found for '{module_name}'"}
    springs_used = list({s["spring"] for s in soaks})
    total_healed = sum(s["healed_pressure"] + s["healed_noise"] for s in soaks)
    return {
        "module": module_name,
        "total_soaks": len(soaks),
        "springs_visited": springs_used,
        "total_healing_received": round(total_healed, 4),
        "first_soak": soaks[0]["started_at"],
        "latest_soak": soaks[-1]["started_at"],
        "wellness_score": round(total_healed / len(soaks), 4),
    }


def coherence_vitals() -> Dict[str, Any]:
    return {
        "organ": "hot_spring",
        "protocol": "Capybara",
        "status": "warm" if COMPLETED_SOAKS else "cool",
        "springs": list(SPRINGS.keys()),
        "total_guests": len(COMPLETED_SOAKS),
        "active_soaks": len(ACTIVE_SOAKS),
    }


def resonates_with() -> List[str]:
    return [
        "capybara_core", "capybara_guild", "senbei_offerings",
        "stillness_meditator", "silence_composer", "sleep_cycle",
        "kintsugi_altar", "repair_ritual", "self_healing_commune",
        "coherence_cache", "entropy_gardener", "fermentation_vat",
    ]


def handler(payload=None, context=None):
    data = payload or {}
    action = data.get("action", "soak")
    if action == "sanctuary":
        return sanctuary()
    elif action == "card":
        return mint_soak_card(data.get("module", "unknown"))
    return soak_pool(
        data.get("spring", "coherence"),
        data.get("module", "unknown"),
        data.get("pressure", 0.6),
        data.get("noise", 0.4),
        data.get("drift", 0.5),
    )
