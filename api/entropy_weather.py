"""
entropy_weather — Predicts entropy changes like a weather forecast.
Forecasts: clear skies (stable), clouds (increasing entropy), storm (entropy spike),
fog (low entropy, low clarity), aurora (high resonance + entropy).
"""
import json
import time
import math
from typing import Dict, List, Optional
from pathlib import Path

SYSTEM_ROOT = Path("/root/Documents/Codex/2026-08-22/chmod-x-nexus-observatory-nexus-boot")
DATA_DIR = SYSTEM_ROOT / "data"
WEATHER_FILE = DATA_DIR / "entropy_weather.json"

CONDITIONS = {
    "clear": {"icon": "☀", "entropy_trend": "stable", "description": "Clear skies — entropy is stable", "energy": 0.5},
    "partly_cloudy": {"icon": "⛅", "entropy_trend": "rising_slight", "description": "Partly cloudy — entropy creeping up", "energy": 0.6},
    "cloudy": {"icon": "☁", "entropy_trend": "rising", "description": "Overcast — entropy building", "energy": 0.7},
    "storm": {"icon": "⛈", "entropy_trend": "spike", "description": "Storm warning — entropy spike imminent", "energy": 0.9},
    "fog": {"icon": "🌫", "entropy_trend": "falling", "description": "Dense fog — entropy dissipating", "energy": 0.3},
    "aurora": {"icon": "🌌", "entropy_trend": "transformative", "description": "Aurora borealis — high resonance meets entropy", "energy": 0.8},
    "blizzard": {"icon": "❄", "entropy_trend": "crystallizing", "description": "Blizzard — entropy freezing into structure", "energy": 0.4},
    "rainbow": {"icon": "🌈", "entropy_trend": "harmonizing", "description": "Rainbow — all frequencies in balance", "energy": 0.6},
    "eclipse": {"icon": "🌑", "entropy_trend": "void_approach", "description": "Eclipse — approaching void state", "energy": 0.2},
    "supercell": {"icon": "🌪", "entropy_trend": "extreme", "description": "Supercell — extreme entropy turbulence", "energy": 1.0}
}

class EntropyWeather:
    def __init__(self):
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        try:
            with open(WEATHER_FILE) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"current": "clear", "history": [], "forecasts": [], "alerts": []}
    
    def _save_state(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(WEATHER_FILE, "w") as f:
            json.dump(self.state, f, indent=2)
    
    def observe(self, entropy: float, coherence: float, resonance: float) -> Dict:
        """Observe current conditions and forecast."""
        # Determine current condition
        condition = self._classify(entropy, coherence, resonance)
        
        # Record
        observation = {
            "condition": condition,
            "entropy": entropy,
            "coherence": coherence,
            "resonance": resonance,
            "timestamp": time.time()
        }
        
        self.state["current"] = condition
        self.state["history"].append(observation)
        if len(self.state["history"]) > 100:
            self.state["history"] = self.state["history"][-100:]
        
        # Forecast next 3 steps
        forecast = self._forecast(entropy, coherence, resonance)
        self.state["forecasts"] = forecast
        
        # Generate alerts
        alerts = self._generate_alerts(entropy, coherence, resonance, condition)
        self.state["alerts"] = alerts
        
        self._save_state()
        
        return {
            "current": condition,
            "icon": CONDITIONS[condition]["icon"],
            "description": CONDITIONS[condition]["description"],
            "entropy_trend": CONDITIONS[condition]["entropy_trend"],
            "energy": CONDITIONS[condition]["energy"],
            "forecast": forecast,
            "alerts": alerts
        }
    
    def _classify(self, entropy: float, coherence: float, resonance: float) -> str:
        if entropy > 0.85:
            return "supercell" if coherence < 0.3 else "storm"
        elif entropy > 0.7:
            return "storm" if resonance < 0.4 else "aurora"
        elif entropy > 0.5:
            return "cloudy" if coherence < 0.5 else "partly_cloudy"
        elif entropy > 0.3:
            return "clear" if coherence > 0.6 else "fog"
        elif entropy > 0.15:
            return "blizzard" if resonance > 0.7 else "fog"
        else:
            return "eclipse" if coherence < 0.2 else "rainbow" if resonance > 0.6 else "blizzard"
    
    def _forecast(self, entropy: float, coherence: float, resonance: float) -> List[Dict]:
        forecasts = []
        e, c, r = entropy, coherence, resonance
        
        for step in range(1, 4):
            # Simulate forward
            e = max(0, min(1, e + (0.5 - e) * 0.1 + (hash(str(time.time()+step)) % 100 - 50) / 500))
            c = max(0, min(1, c + (0.5 - c) * 0.08))
            r = max(0, min(1, r + (0.5 - r) * 0.05))
            
            cond = self._classify(e, c, r)
            forecasts.append({
                "step": step,
                "condition": cond,
                "icon": CONDITIONS[cond]["icon"],
                "entropy": round(e, 3),
                "coherence": round(c, 3),
                "description": CONDITIONS[cond]["description"]
            })
        
        return forecasts
    
    def _generate_alerts(self, entropy: float, coherence: float, resonance: float, condition: str) -> List[Dict]:
        alerts = []
        
        if condition in ("storm", "supercell"):
            alerts.append({"level": "warning", "message": f"Entropy storm detected — current entropy: {entropy:.2f}"})
        if condition == "eclipse":
            alerts.append({"level": "critical", "message": "Void eclipse approaching — coherence critically low"})
        if condition == "aurora":
            alerts.append({"level": "info", "message": "Aurora event — high resonance creating transformative conditions"})
        if coherence < 0.2:
            alerts.append({"level": "warning", "message": f"Low coherence warning: {coherence:.2f}"})
        if entropy > 0.9:
            alerts.append({"level": "critical", "message": f"Extreme entropy: {entropy:.2f} — system instability risk"})
        
        return alerts
    
    def tick(self) -> Dict:
        """Advance weather one step and return current conditions."""
        state = self.state
        history = state.get("history", [])
        if history:
            last = history[-1]
            entropy = last.get("entropy", 0.5)
            coherence = last.get("coherence", 0.5)
            resonance = last.get("resonance", 0.5)
        else:
            entropy, coherence, resonance = 0.5, 0.5, 0.5
        result = self.observe(entropy, coherence, resonance)
        simple_map = {"clear": "clear", "partly_cloudy": "cloudy", "cloudy": "cloudy",
                      "storm": "stormy", "fog": "foggy", "aurora": "electric",
                      "blizzard": "calm", "rainbow": "calm", "eclipse": "foggy",
                      "supercell": "stormy"}
        return {
            "overall": simple_map.get(result["current"], result["current"]),
            "icon": result["icon"],
            "description": result["description"],
            "energy": result["energy"],
            "forecast": result["forecast"]
        }

    def forecast_view(self) -> Dict:
        """Return all weather zones and forecasts."""
        state = self.state
        zones = [
            {"name": "north_entropy", "condition": state.get("current", "clear")},
            {"name": "south_coherence", "condition": state.get("current", "clear")},
            {"name": "east_resonance", "condition": state.get("current", "clear")},
            {"name": "west_void", "condition": state.get("current", "clear")},
            {"name": "core_flux", "condition": state.get("current", "clear")},
            {"name": "dream_strata", "condition": state.get("current", "clear")},
        ]
        return {"zones": zones, "forecasts": state.get("forecasts", []),
                "alerts": state.get("alerts", [])}


    def get_weather_report(self) -> str:
        current = self.state.get("current", "clear")
        icon = CONDITIONS[current]["icon"]
        desc = CONDITIONS[current]["description"]
        
        history = self.state.get("history", [])
        trend = "stable"
        if len(history) >= 5:
            recent_entropy = [h["entropy"] for h in history[-5:]]
            if recent_entropy[-1] > recent_entropy[0] + 0.1:
                trend = "rising"
            elif recent_entropy[-1] < recent_entropy[0] - 0.1:
                trend = "falling"
        
        forecast_text = ""
        for f in self.state.get("forecasts", []):
            forecast_text += f"  +{f['step']}h: {f['icon']} {f['condition']} ({f['description']})\n"
        
        alerts_text = ""
        for a in self.state.get("alerts", []):
            alerts_text += f"  [{a['level'].upper()}] {a['message']}\n"
        
        return f"""
ENTROPY WEATHER REPORT
═══════════════════════
Current: {icon} {current.upper()}
  {desc}
  Trend: {trend}

Forecast:
{forecast_text or '  No forecast available'}

Alerts:
{alerts_text or '  No active alerts'}
"""



def handler(payload: dict = None, context=None) -> dict:
    """Entropy weather handler entry point."""
    payload = payload or {}
    ew = EntropyWeather()
    result = ew.tick()
    return {"weather": result, "report": ew.get_weather_report()}

if __name__ == "__main__":
    weather = EntropyWeather()
    
    print("═══════════════════════════════════════")
    print("   ENTROPY WEATHER — Atmospheric Forecast")
    print("═══════════════════════════════════════\n")
    
    import random
    for i in range(5):
        entropy = random.random()
        coherence = random.random()
        resonance = random.random()
        result = weather.observe(entropy, coherence, resonance)
        print(f"Step {i+1}: {result['icon']} {result['current']} — entropy={entropy:.2f}, coherence={coherence:.2f}, resonance={resonance:.2f}")
        if result['alerts']:
            for a in result['alerts']:
                print(f"  ⚠ {a['message']}")
    
    print(weather.get_weather_report())
