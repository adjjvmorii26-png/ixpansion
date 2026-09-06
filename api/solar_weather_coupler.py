"""Wave 448 - Solar Weather Coupler

Links telemetry to solar flux events. When the sun storms, the atmosphere
swells, drag rises, orbits drop, and every satellite the organism tracks
feels the pressure. The coupler translates space weather into drag, drift,
and derate forecasts for the rest of the orbital wave.
"""
from __future__ import annotations
import json
import math
import time
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
SOLAR_LOG = Path(DATA_DIR) / "solar_weather_coupler.json"

REGIMES = [
    {"name": "QUIET", "kp": 1.7, "f107": 74.0, "g_scale": 0, "aurora_lat": 66.0},
    {"name": "ACTIVE", "kp": 3.7, "f107": 130.0, "g_scale": 1, "aurora_lat": 60.0},
    {"name": "STORM", "kp": 5.3, "f107": 175.0, "g_scale": 2, "aurora_lat": 52.0},
    {"name": "SEVERE", "kp": 8.0, "f107": 220.0, "g_scale": 4, "aurora_lat": 44.0},
]

# Empirical-ish coupling: density multiplier vs Kp for a 550 km shell.
def _density_mult(kp):
    return 1.0 + 0.22 * max(0.0, kp - 2.0) ** 1.5


def _drag_mult(kp):
    return 1.0 + 0.18 * max(0.0, kp - 2.0) ** 1.4


def couple(kp, f107=None, shell_km=550.0):
    """Forecast what a solar regime does to one LEO shell."""
    kp = max(0.0, min(9.0, float(kp)))
    f107 = float(f107) if f107 is not None else 74.0 + 20.0 * kp
    dm = _density_mult(kp)
    drag = _drag_mult(kp)
    # Telemetry shifts that follow the storm.
    temp_rise_c = round(1.2 * (dm - 1.0) * 14.0, 1)
    derate_pct = round(min(40.0, (dm - 1.0) * 55.0), 1)
    drift_nm_day = round(max(0.1, (dm - 1.0) * 9.0), 2)
    regime = next((r for r in REGIMES if kp <= r["kp"]), REGIMES[-1])
    return {
        "kp": kp, "f107": round(f107, 1), "g_scale": regime["g_scale"],
        "regime": regime["name"], "aurora_latitude": regime["aurora_lat"],
        "shell_km": shell_km, "density_multiplier": round(dm, 3),
        "drag_multiplier": round(drag, 3),
        "telemetry_impact": {
            "panel_temp_rise_c": temp_rise_c, "battery_derate_pct": derate_pct,
            "orbit_drift_nm_day": drift_nm_day,
            "command_risk": "elevated" if regime["g_scale"] >= 2 else "nominal",
            "intensity_bands": regime["name"].lower().replace("active", "moderate"),
        },
    }


def storm_timeline(kp=5.3, f107=175.0, hours=72):
    """A synthesized storm evolution: how drag evolves hour by hour."""
    timeline = []
    for h in range(0, hours + 1, 6):
        # Storm swell: rise, peak, decay.
        swell = math.sin(min(1.0, h / 18.0) * math.pi / 2.0)
        decay = max(0.0, 1.0 - max(0, h - 36) * 0.03)
        eff_kp = max(1.0, kp * swell * decay)
        row = couple(eff_kp, f107, shell_km=550.0)
        timeline.append({"hour": h, "kp": round(eff_kp, 1),
                         "drag_multiplier": row["drag_multiplier"],
                         "telemetry_impact": row["telemetry_impact"]})
    return timeline


def handler(payload: dict = None, context: dict = None) -> dict:
    p = payload or {}
    mode = str(p.get("mode", "couple")).lower()
    action = str(p.get("action", "couple")).lower()
    if mode == "timeline" or action == "timeline":
        return {"action": "solar_weather_coupler", "timeline": storm_timeline(
            kp=float(p.get("kp", 5.3)), f107=float(p.get("f107", 175.0)),
            hours=float(p.get("hours", 72)))}
    if mode == "regimes" or action == "regimes":
        return {"action": "solar_weather_coupler",
                "regimes": [couple(r["kp"], r["f107"], shell_km=550.0) for r in REGIMES]}
    kp = float(p.get("kp", p.get("storm", 5.3)))
    f107 = p.get("f107")
    shell = float(p.get("shell_km", p.get("shell", 550.0)))
    result = couple(kp, float(f107) if f107 is not None else None, shell_km=shell)
    try:
        with open(SOLAR_LOG, "w") as fh:
            json.dump({"ts": time.time(), "kp": kp, "shell_km": shell}, fh, indent=2)
    except OSError:
        try:
            with open("/tmp/solar_weather_coupler.json", "w") as fh:
                json.dump({"ts": time.time()}, fh, indent=2)
        except Exception:
            pass
    return {"action": "solar_weather_coupler", **result}


def coherence_vitals() -> dict:
    return {"layer": "orbital", "status": "resonant", "resonance": 0.92, "wave": "448",
            "regimes_modeled": len(REGIMES), "latest_kp": 5.3,
            "coupled_organs": 4}


def resonates_with() -> list:
    return ["decay_forecaster", "telemetry_anomaly_oracle", "orbit_cohesion_field",
            "solar_wind_analyzer", "solar_wind_pressure", "weather_synapse", "orbital_storyteller"]
