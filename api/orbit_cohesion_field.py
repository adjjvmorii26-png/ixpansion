"""Wave 448 - Orbit Cohesion Field

One orbital reality layer for every constellation the organism tracks.
Starlink, OneWeb, and the organism's own sentinel fleet are not separate
objects - they are aspects of a single field. This organ maps that field,
censors fleet constellations, and computes pairwise conjunction risk so the
organism can watch the sky the way it watches its own modules.

The organism's constellation-awareness layer: all tracked objects, unified.
"""
from __future__ import annotations
import json
import math
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

DATA_DIR = Path(__file__).parent.parent / "data"
COHESION_LOG = Path(DATA_DIR) / "orbit_cohesion_field.json"

EARTH_RADIUS_KM = 6371.0
MU_KM3_S2 = 398600.4418  # Earth gravitational parameter

RISK_GREEN = 1e-6
RISK_YELLOW = 1e-4
RISK_RED = 1e-3
CLOSE_ALT_KM = 25.0
NEAR_MISS_KM = 10.0
VEL_TOLERANCE_KM_S = 5.0

# Reference fleets the constellation mapper tracks.
FLEET_SHELLS = {
    "STARLINK": {"alt": 550.0, "incl_deg": 53.0, "n": 8, "prefix": "STLK"},
    "ONEWEB": {"alt": 1200.0, "incl_deg": 87.4, "n": 6, "prefix": "ONEW"},
    "IXP-SENTINEL": {"alt": 800.0, "incl_deg": 42.0, "n": 4, "prefix": "IXPS"},
}


@dataclass
class SatelliteTrace:
    """A satellite's path through orbital space over time."""
    satellite_id: str
    name: str
    timestamps: list
    latitudes: list
    longitudes: list
    altitudes: list
    velocities: list

    def __len__(self):
        return len(self.timestamps)


def _kinematic_params(alt_km: float):
    """Circular-orbit angular rate and speed for a shell altitude."""
    r = EARTH_RADIUS_KM + alt_km
    omega = math.sqrt(MU_KM3_S2 / r ** 3)  # rad/s
    v = math.sqrt(MU_KM3_S2 / r)           # km/s
    return omega, v


def demo_constellations(now: Optional[float] = None) -> list:
    """Synthesize deterministic demo traces for all tracked fleets.

    Each trace is a spherical-orbit parametrization: latitude follows the
    inclination, longitude drifts with the orbital phase. Used as the
    organism's stand-in for real TLE data until the domain uplink arrives.
    """
    now = now if now is not None else time.time()
    traces = []
    for fleet, cfg in FLEET_SHELLS.items():
        alt = cfg["alt"]
        incl = math.radians(cfg["incl_deg"])
        n = cfg["n"]
        omega, v = _kinematic_params(alt)
        for i in range(n):
            sid = f"{cfg['prefix']}-{i + 1:04d}"
            base_lon = (i * 360.0 / n) - 180.0
            phase = (i * 137.5) % 360.0  # golden-angle phasing across the fleet
            ts, lats, lons, alts, vels = [], [], [], [], []
            for k in range(24):
                t = now + k * 300.0
                ang = omega * (t - now) + math.radians(phase)
                lat = math.degrees(math.asin(math.sin(incl) * math.sin(ang)))
                lon = math.degrees(math.atan2(math.cos(incl) * math.sin(ang), math.cos(ang))) + base_lon
                lon = (lon + 540.0) % 360.0 - 180.0
                ts.append(t)
                lats.append(round(lat, 3))
                lons.append(round(lon, 3))
                alts.append(round(alt + 2.5 * math.sin(2 * ang), 2))
                vels.append(round(v * (1 + 0.004 * math.sin(2 * ang)), 4))
            traces.append(SatelliteTrace(sid, f"{fleet.lower()}-{sid.lower()}", ts, lats, lons, alts, vels))
    return traces


def _find_trace(traces, key: str) -> Optional[SatelliteTrace]:
    key = key.upper()
    import re as _re
    for s in traces:
        if key in s.satellite_id.upper() or key in s.name.upper():
            return s
    m = _re.match(r"([A-Z]+)-?0*(\d+)$", key)
    if m:
        prefix, num = m.group(1), int(m.group(2))
        for s in traces:
            sm = _re.match(r"([A-Z]+)-0*(\d+)$", s.satellite_id.upper())
            if sm and sm.group(1) == prefix and int(sm.group(2)) == num:
                return s
    return None


def compute_orbital_state(t: float, sat: SatelliteTrace) -> Optional[dict]:
    """Interpolate a satellite's state at a given epoch time."""
    ts = sat.timestamps
    if not ts or t < ts[0]:
        return None
    if t >= ts[-1]:
        i = len(ts) - 2
    else:
        lo, hi = 0, len(ts) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if ts[mid] < t:
                lo = mid + 1
            else:
                hi = mid
        i = lo - 1
    if i < 0 or i >= len(ts) - 1:
        return None
    t0, t1 = ts[i], ts[i + 1]
    f = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
    lerp = lambda a, b: a + f * (b - a)
    return {
        "timestamp": t,
        "latitude": lerp(sat.latitudes[i], sat.latitudes[i + 1]),
        "longitude": lerp(sat.longitudes[i], sat.longitudes[i + 1]),
        "altitude": lerp(sat.altitudes[i], sat.altitudes[i + 1]),
        "velocity": lerp(sat.velocities[i], sat.velocities[i + 1]),
    }


def _geo_distance_km(a: dict, b: dict) -> float:
    """Straight-line separation between two orbital states (km)."""
    lat_a, lon_a = math.radians(a["latitude"]), math.radians(a["longitude"])
    lat_b, lon_b = math.radians(b["latitude"]), math.radians(b["longitude"])
    r_a = EARTH_RADIUS_KM + a["altitude"]
    r_b = EARTH_RADIUS_KM + b["altitude"]
    xa = r_a * math.cos(lat_a) * math.cos(lon_a)
    ya = r_a * math.cos(lat_a) * math.sin(lon_a)
    za = r_a * math.sin(lat_a)
    xb = r_b * math.cos(lat_b) * math.cos(lon_b)
    yb = r_b * math.cos(lat_b) * math.sin(lon_b)
    zb = r_b * math.sin(lat_b)
    return math.sqrt((xa - xb) ** 2 + (ya - yb) ** 2 + (za - zb) ** 2)


def compute_conjunction(a: SatelliteTrace, b: SatelliteTrace, samples: int = 240) -> dict:
    """Stratified conjunction scan over the shared observation window."""
    if len(a) < 2 or len(b) < 2:
        return {"sat_a": a.satellite_id, "sat_b": b.satellite_id, "probability": 1.0,
                "closest_approach_km": 0.0, "risk_level": "critical", "near_misses": samples}
    t_min = max(a.timestamps[0], b.timestamps[0])
    t_max = min(a.timestamps[-1], b.timestamps[-1])
    if t_min >= t_max:
        return {"sat_a": a.satellite_id, "sat_b": b.satellite_id, "probability": 1.0,
                "closest_approach_km": 0.0, "risk_level": "critical", "near_misses": samples}
    closest, closest_t = float("inf"), t_min
    near_misses = 0
    for i in range(samples):
        t = t_min + (t_max - t_min) * i / (samples - 1)
        sa, sb = compute_orbital_state(t, a), compute_orbital_state(t, b)
        if sa is None or sb is None:
            continue
        d = _geo_distance_km(sa, sb)
        if d < closest:
            closest, closest_t = d, t
        if d < NEAR_MISS_KM and abs(sa["velocity"] - sb["velocity"]) < VEL_TOLERANCE_KM_S:
            near_misses += 1
    prob = near_misses / samples
    # Closeness itself raises the risk ceiling, even without a counted near miss.
    if closest < CLOSE_ALT_KM:
        prob = max(prob, 1.0 - closest / CLOSE_ALT_KM)
    risk = "green"
    if prob >= 0.25:
        risk = "critical"
    elif prob >= RISK_RED:
        risk = "red"
    elif prob >= RISK_YELLOW:
        risk = "yellow"
    elif prob > RISK_GREEN:
        risk = "amber"
    return {"sat_a": a.satellite_id, "sat_b": b.satellite_id,
            "probability": round(min(prob, 1.0), 6),
            "closest_approach_km": round(closest, 2),
            "time_of_closest": closest_t, "risk_level": risk,
            "near_misses": near_misses}


def constellation_census(traces: list) -> dict:
    """Constellation Mapper mode - fleet-level census of every tracked family."""
    prefix_to_fleet = {cfg["prefix"]: fleet for fleet, cfg in FLEET_SHELLS.items()}
    fleets = {}
    for s in traces:
        fleet = prefix_to_fleet.get(s.satellite_id.split("-")[0], s.satellite_id.split("-")[0])
        entry = fleets.setdefault(fleet, {"count": 0, "altitudes": []})
        entry["count"] += 1
        entry["altitudes"].append(round(sum(s.altitudes) / len(s.altitudes), 1))
    census = []
    for fleet, entry in fleets.items():
        cfg = FLEET_SHELLS.get(fleet, {})
        census.append({
            "fleet": fleet,
            "count": entry["count"],
            "shell_km": round(sum(entry["altitudes"]) / len(entry["altitudes"]), 1),
            "inclination_deg": cfg.get("incl_deg", 0),
            "phase_diversity": round(90.0, 1),
            "traffic_density": round(entry["count"] * 100.0 / max(360.0, entry["count"] * 7.2), 3),
        })
    census.sort(key=lambda c: -c["count"])
    return {"action": "constellation_census", "fleets": census, "total_objects": len(traces)}


def orbit_cohesion_field(satellites: list, threshold_probability: float = RISK_YELLOW) -> dict:
    """Generate the unified cohesion field over all tracked objects."""
    n = len(satellites)
    if n < 2:
        return {"action": "orbit_cohesion_field", "field_strength": 1.0, "total_pairs": 0,
                "conjunctions": [], "high_risk": [], "mean_probability": 0.0,
                "total_objects": n, "timestamp": time.time()}
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            pairs.append(compute_conjunction(satellites[i], satellites[j]))
    pairs.sort(key=lambda p: -p["probability"])
    high_risk = [p for p in pairs if p["probability"] > threshold_probability]
    mean_p = sum(p["probability"] for p in pairs) / len(pairs)
    if high_risk:
        worst = max(p["probability"] for p in high_risk)
        field_strength = round(max(0.0, 1.0 - worst * 2.0), 4)
    else:
        field_strength = round(max(0.4, 1.0 - mean_p * 500.0), 4)
    return {
        "action": "orbit_cohesion_field",
        "field_strength": field_strength,
        "total_pairs": len(pairs),
        "conjunctions": pairs,
        "high_risk": high_risk,
        "mean_probability": round(mean_p, 6),
        "total_objects": n,
        "nominal_risk": "yellow" if high_risk else "green",
        "timestamp": time.time(),
    }


def _overhead(traces: list, lat: float, lon: float, t: Optional[float] = None) -> list:
    """Which tracked objects are visible from a point on the ground right now."""
    t = t if t is not None else time.time()
    out = []
    for s in traces:
        st = compute_orbital_state(t, s)
        if st is None:
            continue
        max_ang = math.acos(EARTH_RADIUS_KM / (EARTH_RADIUS_KM + st["altitude"]))
        dlon = math.radians(st["longitude"] - lon)
        sep = math.acos(max(-1.0, min(1.0, math.sin(math.radians(lat)) * math.sin(math.radians(st["latitude"]))
                                      + math.cos(math.radians(lat)) * math.cos(math.radians(st["latitude"]))
                                      * math.cos(dlon))))
        if sep <= max_ang:
            out.append({"satellite": s.satellite_id, "altitude_km": round(st["altitude"], 1),
                        "sub_lat": round(st["latitude"], 2), "sub_lon": round(st["longitude"], 2),
                        "separation_deg": round(math.degrees(sep), 1)})
    return sorted(out, key=lambda o: o["separation_deg"])


def _remember(entry: dict) -> None:
    state = []
    for p in (COHESION_LOG, Path("/tmp") / "orbit_cohesion_field.json"):
        try:
            with open(p) as fh:
                state = json.load(fh)
            break
        except Exception:
            pass
    state.append(entry)
    state = state[-40:]
    try:
        os.makedirs(COHESION_LOG.parent, exist_ok=True)
        with open(COHESION_LOG, "w") as fh:
            json.dump(state, fh, indent=2)
    except OSError:
        try:
            with open(Path("/tmp") / "orbit_cohesion_field.json", "w") as fh:
                json.dump(state, fh, indent=2)
        except Exception:
            pass


def handler(payload: dict = None, context: dict = None) -> dict:
    p = payload or {}
    action = str(p.get("action", p.get("mode", "field"))).lower()
    now = p.get("now") if isinstance(p.get("now"), (int, float)) else None
    traces = demo_constellations(now)
    try:
        if action in ("fleets", "constellations", "constellation", "census", "mapper"):
            result = constellation_census(traces)
        elif action in ("pair", "conjunction"):
            a = _find_trace(traces, str(p.get("a", "STLK-1")))
            b = _find_trace(traces, str(p.get("b", "ONEW-1")))
            if not a or not b:
                return {"action": action, "error": "satellite not found",
                        "known": [s.satellite_id for s in traces]}
            result = {"action": "pair_conjunction", "sat_a": a.satellite_id, "sat_b": b.satellite_id,
                      "assessment": compute_conjunction(a, b)}
        elif action in ("overhead", "sky"):
            lat, lon = float(p.get("lat", 40.71)), float(p.get("lon", -74.0))
            result = {"action": "overhead", "lat": lat, "lon": lon,
                      "objects": _overhead(traces, lat, lon, now)}
        else:
            result = orbit_cohesion_field(traces)
            result["census"] = constellation_census(traces)
    except Exception as e:  # never let one bad mode sink the organ
        result = {"action": action, "error": str(e)}
    _remember({"action": action, "ts": time.time(),
               "summary": str(result.get("field_strength", result.get("total_objects", "")))})
    return result


def coherence_vitals() -> dict:
    try:
        traces = demo_constellations()
        field = orbit_cohesion_field(traces, threshold_probability=RISK_RED)
        strength = field.get("field_strength", 0.5)
        return {
            "layer": "orbital",
            "status": "resonant" if strength > 0.6 else "drifting",
            "resonance": round(strength, 3),
            "wave": "448",
            "tracked_objects": len(traces),
            "high_risk": len(field.get("high_risk", [])),
        }
    except Exception:
        return {"layer": "orbital", "status": "drifting", "resonance": 0.3, "wave": "448",
                "tracked_objects": 0, "high_risk": 0}


def resonates_with() -> list:
    return ["telemetry_parser", "live_telemetry", "constellation_topology", "decay_forecaster",
            "debris_field_mapper", "solar_weather_coupler", "orbital_storyteller",
            "telemetry_anomaly_oracle", "ground_station_synthesizer", "noise_filter"]
