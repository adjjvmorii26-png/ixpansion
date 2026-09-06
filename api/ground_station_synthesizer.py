"""Wave 448 - Ground Station Synthesizer

Simulates satellite passes from an arbitrary latitude/longitude: visibility
windows, maximum elevation, azimuth, and next-pass countdowns. It is a
synthesizer, not a propagator - a stand-in sky for stations the organism
has not yet met.
"""
from __future__ import annotations
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
STATION_LOG = Path(DATA_DIR) / "ground_station_synthesizer.json"

EARTH_RADIUS_KM = 6371.0
MU_KM3_S2 = 398600.4418


def _orbit_params(alt_km):
    r = EARTH_RADIUS_KM + alt_km
    return math.sqrt(MU_KM3_S2 / r ** 3), math.sqrt(MU_KM3_S2 / r), r


def _sat_positions(prefix, alt_km, incl_deg, n, t0, hours):
    """Deterministic pseudo-TLE: sub-satellite lat/lon per satellite over time."""
    incl = math.radians(incl_deg)
    omega, _, _ = _orbit_params(alt_km)
    out = []
    for i in range(n):
        sid = f"{prefix}-{i + 1:04d}"
        base_lon = (i * 360.0 / n) - 180.0
        phase = (i * 137.5) % 360.0
        samples = []
        steps = max(4, int(hours * 60 // 10))
        for k in range(steps + 1):
            t = t0 + k * 600.0
            ang = omega * (t - t0) + math.radians(phase)
            lat = math.degrees(math.asin(math.sin(incl) * math.sin(ang)))
            lon = math.degrees(math.atan2(math.cos(incl) * math.sin(ang), math.cos(ang))) + base_lon
            lon = (lon + 540.0) % 360.0 - 180.0
            samples.append((t, lat, lon))
        out.append({"id": sid, "samples": samples})
    return out


def synthesize(lat, lon, fleet="STARLINK", hours=24.0, n=5):
    """Compute the pass schedule for a fleet as seen from a ground station."""
    configs = {
        "STARLINK": {"alt": 550.0, "incl": 53.0, "prefix": "STLK"},
        "ONEWEB": {"alt": 1200.0, "incl": 87.4, "prefix": "ONEW"},
        "IXP-SENTINEL": {"alt": 800.0, "incl": 42.0, "prefix": "IXPS"},
        "CUSTOM": {"alt": 800.0, "incl": 42.0, "prefix": "IXPS"},
    }
    cfg = configs.get(str(fleet).upper(), configs["STARLINK"])
    alt, incl_deg, prefix = cfg["alt"], cfg["incl"], cfg["prefix"]
    t0 = time.time()
    sats = _sat_positions(prefix, alt, incl_deg, n, t0, hours)
    lat_r, lon_r = math.radians(lat), math.radians(lon)
    horizon = math.acos(EARTH_RADIUS_KM / (EARTH_RADIUS_KM + alt))  # max ground angle
    passes = []
    for sat in sats:
        active = False
        start = peak_el = start_el = None
        peak_az = 0.0
        for (t, slat, slon) in sat["samples"]:
            slat_r, slon_r = math.radians(slat), math.radians(slon)
            c = (math.sin(lat_r) * math.sin(slat_r)
                 + math.cos(lat_r) * math.cos(slat_r) * math.cos(slon_r - lon_r))
            c = max(-1.0, min(1.0, c))
            ang = math.acos(c)
            if ang <= horizon:
                # elevation from slant geometry
                el = math.degrees(math.atan2(math.cos(ang) - EARTH_RADIUS_KM / (EARTH_RADIUS_KM + alt),
                                             math.sin(ang)))
                az = math.degrees(math.atan2(math.sin(slon_r - lon_r) * math.cos(slat_r),
                                             math.cos(lat_r) * math.sin(slat_r)
                                             - math.sin(lat_r) * math.cos(slat_r) * math.cos(slon_r - lon_r)))
                if not active:
                    active, start, start_el = True, t, el
                    peak_el, peak_az = el, az
                elif el > peak_el:
                    peak_el, peak_az = el, az
            elif active:
                passes.append({
                    "satellite": sat["id"], "start": datetime.fromtimestamp(start, timezone.utc).isoformat(),
                    "end": datetime.fromtimestamp(t, timezone.utc).isoformat(),
                    "duration_min": round((t - start) / 60.0, 1),
                    "max_elevation_deg": round(peak_el, 1),
                    "azimuth_at_peak_deg": round((peak_az + 360) % 360, 1),
                    "countdown_s": int(max(0.0, start - t0)),
                })
                active = False
        if active:
            end_t = sat["samples"][-1][0]
            passes.append({
                "satellite": sat["id"], "start": datetime.fromtimestamp(start, timezone.utc).isoformat(),
                "end": datetime.fromtimestamp(end_t, timezone.utc).isoformat(),
                "duration_min": round((end_t - start) / 60.0, 1),
                "max_elevation_deg": round(peak_el, 1),
                "azimuth_at_peak_deg": round((peak_az + 360) % 360, 1),
                "countdown_s": int(max(0.0, start - t0)),
            })
    passes.sort(key=lambda p: p["countdown_s"])
    visible = [p for p in passes if p["max_elevation_deg"] >= 10.0][:8]
    return {
        "action": "ground_station_synthesis", "station": {"lat": lat, "lon": lon},
        "fleet": str(fleet).upper(), "shell_km": alt, "horizon_deg": round(math.degrees(horizon), 1),
        "window_hours": hours, "passes_computed": len(passes), "next_passes": visible,
        "next_in_s": visible[0]["countdown_s"] if visible else None,
    }


def handler(payload: dict = None, context: dict = None) -> dict:
    p = payload or {}
    mode = str(p.get("mode", "synthesize")).lower()
    if mode == "stations":
        stations = [
            {"name": "ALEPH-HOME", "lat": 40.71, "lon": -74.0, "fleet": "STARLINK"},
            {"name": "MORII-OBSERVATORY", "lat": 51.5, "lon": -0.12, "fleet": "ONEWEB"},
            {"name": "SENTINEL-PRIME", "lat": -33.86, "lon": 151.21, "fleet": "IXP-SENTINEL"},
        ]
        results = []
        for s in stations:
            r = synthesize(s["lat"], s["lon"], s["fleet"], hours=float(p.get("hours", 24.0)),
                           n=int(p.get("n", 5)))
            r["station"] = {"name": s["name"], "lat": s["lat"], "lon": s["lon"]}
            results.append(r)
        return {"action": "ground_station_synthesis", "mode": "stations", "stations": results}
    return synthesize(float(p.get("lat", 40.71)), float(p.get("lon", -74.0)),
                      str(p.get("fleet", "STARLINK")), hours=float(p.get("hours", 24.0)),
                      n=int(p.get("n", 5)))


def coherence_vitals() -> dict:
    return {"layer": "orbital", "status": "resonant", "resonance": 0.85, "wave": "448",
            "stations_synthesized": 3, "horizon_model": "spherical"}


def resonates_with() -> list:
    return ["orbit_cohesion_field", "constellation_topology", "orbital_storyteller",
            "telemetry_parser", "live_telemetry", "constellation_cartographer"]
