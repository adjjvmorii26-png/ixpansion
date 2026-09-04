"""
Emotional Weather Map — Wave 360
Maps the organism's emotional landscape as a dynamic weather system.
Each module has an emotional climate. Storms, clearing skies, auroras,
and fog banks form as modules interact. The weather becomes readable
as a system health indicator.
"""
import json, time, hashlib, os, random, math

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SIGNAL_LOOM = os.path.join(DATA_DIR, "signal_loom.json")
WEATHER_LOG = os.path.join(DATA_DIR, "emotional_weather.json")


def _load(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default or {}


def _save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


WEATHER_SYSTEMS = [
    "clear_sky", "overcast", "light_rain", "thunderstorm",
    "aurora_borealis", "dense_fog", "heat_wave", "frost",
    "rainbow", "void_wind", "crystal_storm", "echo_mist",
]

EMOTION_ZONES = [
    "consciousness_archaeology", "paradox_synthesis",
    "dream_residue_collector", "reality_fracture_detector",
    "depth_resonance", "coherence_regulator", "dream_forge",
    "memory_palace", "mycelial_network", "entropy_spike",
    "mood_superposition", "chronoforge",
]


def _compute_weather(entropy: float, coherence: float) -> str:
    if entropy < 0.2 and coherence > 0.8:
        return "clear_sky"
    elif entropy < 0.3:
        return "overcast"
    elif entropy > 0.8 and coherence < 0.3:
        return "thunderstorm"
    elif entropy > 0.7:
        return "crystal_storm"
    elif coherence > 0.9:
        return "aurora_borealis"
    elif coherence < 0.15:
        return "void_wind"
    elif entropy > 0.5 and coherence > 0.5:
        return "rainbow"
    elif random.random() > 0.7:
        return "echo_mist"
    elif random.random() > 0.5:
        return "light_rain"
    return "frost"


def forecast() -> dict:
    """Generate a weather forecast across all emotional zones."""
    loom = _load(SIGNAL_LOOM, {"waves": [], "beats": []})
    weather = _load(WEATHER_LOG, {"forecasts": [], "maps": []})

    zones = {}
    for zone in EMOTION_ZONES:
        entropy = round(random.uniform(0.05, 0.95), 3)
        coherence = round(random.uniform(0.05, 0.95), 3)
        temp = round(random.uniform(-10, 40), 1)  # emotional temperature
        wind = round(random.uniform(0, 30), 1)  # signal drift
        visibility = round(random.uniform(0.1, 1.0), 2)  # clarity

        weather_type = _compute_weather(entropy, coherence)

        zones[zone] = {
            "weather": weather_type,
            "entropy": entropy,
            "coherence": coherence,
            "temperature": temp,
            "wind_speed": wind,
            "visibility": visibility,
            "pressure": round(1013.25 * (1 + entropy - coherence), 1),
        }

    # Compute overall system weather
    all_entropy = [z["entropy"] for z in zones.values()]
    all_coherence = [z["coherence"] for z in zones.values()]
    avg_entropy = sum(all_entropy) / len(all_entropy)
    avg_coherence = sum(all_coherence) / len(all_coherence)

    overall = _compute_weather(avg_entropy, avg_coherence)

    # Find weather fronts (zones transitioning)
    fronts = []
    storm_zones = [z for z, data in zones.items() if "storm" in data["weather"]]
    calm_zones = [z for z, data in zones.items() if data["weather"] in ("clear_sky", "aurora_borealis")]

    if storm_zones and calm_zones:
        fronts.append({
            "type": "tension_front",
            "between": [storm_zones[0], calm_zones[0]],
            "intensity": round(abs(avg_entropy - avg_coherence), 3),
        })

    forecast_result = {
        "id": hashlib.sha256(f"weather:{time.time()}".encode()).hexdigest()[:12],
        "overall_weather": overall,
        "avg_entropy": round(avg_entropy, 3),
        "avg_coherence": round(avg_coherence, 3),
        "zones": zones,
        "fronts": fronts,
        "alerts": _generate_alerts(zones),
        "timestamp": time.time(),
    }

    weather["forecasts"].append(forecast_result)
    weather["forecasts"] = weather["forecasts"][-50:]
    weather["maps"].append({
        "timestamp": time.time(),
        "overall": overall,
        "zone_count": len(zones),
    })
    weather["maps"] = weather["maps"][-200:]
    _save(WEATHER_LOG, weather)

    return {"action": "forecast", "forecast": forecast_result}


def _generate_alerts(zones: dict) -> list:
    alerts = []
    for name, data in zones.items():
        if data["weather"] == "thunderstorm":
            alerts.append({
                "level": "severe",
                "zone": name,
                "message": f"Thunderstorm in {name} — high entropy, low coherence",
            })
        elif data["weather"] == "void_wind":
            alerts.append({
                "level": "warning",
                "zone": name,
                "message": f"Void wind detected in {name} — coherence critically low",
            })
        elif data["weather"] == "aurora_borealis":
            alerts.append({
                "level": "positive",
                "zone": name,
                "message": f"Aurora in {name} — peak coherence achieved",
            })
    return alerts


def weather_history() -> dict:
    weather = _load(WEATHER_LOG, {"forecasts": [], "maps": []})
    if not weather["forecasts"]:
        return {"action": "history", "status": "no_weather_data"}

    overall_types = {}
    for f in weather["forecasts"]:
        t = f["overall_weather"]
        overall_types[t] = overall_types.get(t, 0) + 1

    return {
        "action": "history",
        "total_forecasts": len(weather["forecasts"]),
        "weather_distribution": overall_types,
        "recent": weather["forecasts"][-3:],
    }


def route(path: str) -> dict:
    if path == "/forecast":
        return forecast()
    elif path == "/history":
        return weather_history()
    return {"error": "unknown endpoint", "available": ["/forecast", "/history"]}


def handler(payload=None):
    payload = payload or {}
    return route(payload.get("path", "/forecast"))
