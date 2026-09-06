"""Wave 448 - Decay Forecaster

Predicts re-entry windows for tracked objects. Drag, solar flux coupling,
and ballistic coefficient decide when an orbit surrenders to the atmosphere.
The organism watches its constellation age the way it watches its modules.
"""
from __future__ import annotations
import json
import math
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DECAY_LOG = Path(DATA_DIR) / "decay_forecaster.json"

EARTH_RADIUS_M = 6371000.0
MU_M3_S2 = 3.986004418e14
CD = 2.2
DEMISE_ALT_KM = 120.0
MAX_YEARS = 6

# Approximate atmospheric density by altitude shell (kg/m3), log-interpolated.
RHO_TABLE = [
    (100, 4.4e-7), (150, 2.0e-9), (200, 2.5e-10), (300, 2.0e-11),
    (400, 3.9e-12), (500, 1.0e-12), (600, 3.5e-13), (800, 7.5e-14),
    (1000, 2.2e-14), (1200, 9.0e-15), (1500, 4.5e-15),
]


def rho_at(alt_km):
    if alt_km <= RHO_TABLE[0][0]:
        return RHO_TABLE[0][1]
    if alt_km >= RHO_TABLE[-1][0]:
        return RHO_TABLE[-1][1]
    for (h0, r0), (h1, r1) in zip(RHO_TABLE, RHO_TABLE[1:]):
        if h0 <= alt_km <= h1:
            f = (alt_km - h0) / (h1 - h0)
            return math.exp(math.log(r0) * (1 - f) + math.log(r1) * f)
    return RHO_TABLE[-1][1]


def solar_density_multiplier(kp):
    """Couple to solar weather: density enhancement from geomagnetic activity."""
    return 1.0 + 0.22 * max(0.0, kp - 2.0) ** 1.5


def forecast(altitude_km, mass_kg, area_m2, kp=3.0, max_alt_tolerance_km=0.1):
    """Integrate drag decay day by day until the demise altitude.

    Returns days-to-re-entry, a window, remaining orbits, and the drag story.
    """
    h = float(altitude_km)
    mass = max(0.1, float(mass_kg))
    area = max(0.01, float(area_m2))
    bal = area / mass  # m2/kg
    kp = max(0.0, float(kp))
    days = 0
    start_h = h
    while h > DEMISE_ALT_KM and days < int(MAX_YEARS * 365.25):
        r = EARTH_RADIUS_M + h * 1000.0
        v = math.sqrt(MU_M3_S2 / r)
        accel = 0.5 * rho_at(h) * solar_density_multiplier(kp) * CD * bal * v * v
        da_dt = -2.0 * (r / v) * accel  # m/s
        drop_m = abs(da_dt) * 86400.0
        drop_km = drop_m / 1000.0
        h -= drop_km
        days += 1
        if drop_km < 1e-6:
            h -= 0.01  # ensure progress in dead-quiet regimes
    reentry = datetime.now(timezone.utc) + timedelta(days=days)
    period_s = 2.0 * math.pi * math.sqrt((EARTH_RADIUS_M + h * 1000.0) ** 3 / MU_M3_S2)
    orbits_remaining = int(days * 86400.0 / period_s)
    spread = max(2, int(days * 0.06))  # forecast uncertainty grows with lifetime
    return {
        "action": "decay_forecast",
        "input": {"altitude_km": start_h, "mass_kg": mass, "area_m2": area,
                  "ballistic_coef_m2_kg": round(bal, 4), "kp": kp},
        "days_to_reentry": days,
        "reentry_window_start": (reentry - timedelta(days=spread)).isoformat(),
        "reentry_window_end": (reentry + timedelta(days=spread)).isoformat(),
        "nominal_reentry": reentry.isoformat(),
        "orbits_remaining": orbits_remaining,
        "decay_rate_km_day": round((start_h - h) / max(1, days), 4),
        "demise_altitude_km": DEMISE_ALT_KM,
        "drag_regime": "high" if (start_h - h) / max(1, days) > 0.5 else
                       ("moderate" if (start_h - h) / max(1, days) > 0.05 else "slow"),
        "solar_coupling_kp": kp,
        "forecast_uncertainty_days": spread,
    }


def forecast_fleet():
    """A decay prognosis for the organism's tracked families."""
    bodies = [
        {"id": "STLK-1010", "altitude_km": 550.0, "mass_kg": 260.0, "area_m2": 5.6, "kp": 3.0},
        {"id": "ONEW-0442", "altitude_km": 1200.0, "mass_kg": 150.0, "area_m2": 3.2, "kp": 3.0},
        {"id": "IXPS-0001", "altitude_km": 800.0, "mass_kg": 340.0, "area_m2": 5.0, "kp": 3.0},
        {"id": "DEBRIS-53432", "altitude_km": 430.0, "mass_kg": 14.0, "area_m2": 1.2, "kp": 3.0},
    ]
    return [{"object": b["id"], **forecast(**b)} for b in bodies]


def handler(payload: dict = None, context: dict = None) -> dict:
    p = payload or {}
    action = str(p.get("action", "forecast")).lower()
    if action in ("fleet", "all", "reports"):
        out = forecast_fleet()
    elif action == "storm":
        base = forecast(float(p.get("altitude_km", 500.0)),
                        float(p.get("mass_kg", 260.0)), float(p.get("area_m2", 5.6)), kp=8.0)
        calm = forecast(float(p.get("altitude_km", 500.0)),
                        float(p.get("mass_kg", 260.0)), float(p.get("area_m2", 5.6)), kp=2.0)
        base["comparison"] = {
            "quiet_kp2_would_survive_days": calm["days_to_reentry"],
            "storm_kp8_reentry_days": base["days_to_reentry"],
            "differential_days": calm["days_to_reentry"] - base["days_to_reentry"],
        }
        out = base
    else:
        out = forecast(float(p.get("altitude_km", p.get("altitude", 550.0))),
                       float(p.get("mass_kg", 260.0)), float(p.get("area_m2", 5.6)),
                       kp=float(p.get("kp", 3.0)))
    try:
        _log = json.loads(open(DECAY_LOG).read()) if DECAY_LOG.exists() else []
        _log.append({"ts": time.time(), "objects": len(out) if isinstance(out, list) else 1})
        open(DECAY_LOG, "w").write(json.dumps(_log[-50:], indent=2))
    except Exception:
        try:
            open("/tmp/decay_forecaster.json", "w").write(json.dumps(out, indent=2))
        except Exception:
            pass
    return out


def coherence_vitals() -> dict:
    return {"layer": "orbital", "status": "resonant", "resonance": 0.91, "wave": "448",
            "tracked_for_decay": 4, "demise_altitude_km": DEMISE_ALT_KM}


def resonates_with() -> list:
    return ["orbit_cohesion_field", "solar_weather_coupler", "debris_field_mapper",
            "telemetry_anomaly_oracle", "orbital_storyteller", "telemetry_parser"]
