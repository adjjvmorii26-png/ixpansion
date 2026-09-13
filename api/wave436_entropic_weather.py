"""Wave 436 — Entropic Weather.

The organism now has weather. Not metaphorical weather — actual
computational weather patterns that affect every module differently.

- Clear skies: low entropy, high stability, modules run predictably
- Storms: high entropy, mutations spike, creative bursts
- Fog: uncertainty rises, new patterns emerge from noise
- Aurora: creative mode, aesthetic algorithms activate
- Drought: entropy exhaustion, modules slow down and conserve
- Monsoon: cascade of events, everything connects to everything

Each weather event has a pressure system, temperature, and wind pattern.
Modules respond to weather based on their temperament.
"""
from __future__ import annotations
import json, time, random, math, hashlib
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave436_entropic_weather.json"

WEATHER_TYPES = {
    "clear": {"entropy_mod": -0.1, "creativity": 0.2, "stability": 0.9, "mutation_rate": 0.01},
    "storm": {"entropy_mod": 0.3, "creativity": 0.8, "stability": 0.3, "mutation_rate": 0.15},
    "fog": {"entropy_mod": 0.1, "creativity": 0.6, "stability": 0.5, "mutation_rate": 0.08},
    "aurora": {"entropy_mod": 0.05, "creativity": 1.0, "stability": 0.7, "mutation_rate": 0.05},
    "drought": {"entropy_mod": -0.2, "creativity": 0.1, "stability": 0.95, "mutation_rate": 0.005},
    "monsoon": {"entropy_mod": 0.4, "creativity": 0.7, "stability": 0.2, "mutation_rate": 0.2},
}


class WeatherCell:
    """A single weather cell in the organism's atmosphere."""

    def __init__(self, cell_id: str, weather_type: str = "clear"):
        self.cell_id = cell_id
        self.weather_type = weather_type
        self.pressure = 1013.25
        self.temperature = 20.0
        self.wind_speed = 0.0
        self.wind_direction = 0.0
        self.humidity = 0.5
        self.entropy = 0.2
        self.creativity = 0.2
        self.stability = 0.9
        self.mutation_rate = 0.01
        self.age = 0
        self.created = time.time()
        self._apply_weather()

    def _apply_weather(self):
        props = WEATHER_TYPES.get(self.weather_type, WEATHER_TYPES["clear"])
        self.entropy = max(0, min(1, self.entropy + props["entropy_mod"]))
        self.creativity = props["creativity"]
        self.stability = props["stability"]
        self.mutation_rate = props["mutation_rate"]
        self.pressure = 1013.25 + (props["entropy_mod"] * 50)
        self.temperature = 20 + (self.creativity * 30 - 15)
        self.wind_speed = props["entropy_mod"] * 20
        self.wind_direction = random.uniform(0, 360)
        self.humidity = 0.3 + self.entropy * 0.6

    def advance(self) -> dict | None:
        """Advance the weather cell one tick. May trigger a weather change."""
        self.age += 1
        transition_chance = 0.05 + self.entropy * 0.1

        if random.random() < transition_chance:
            return self._transition()
        return None

    def _transition(self) -> dict:
        """Transition to a new weather type based on current pressure."""
        weights = {}
        for wtype, props in WEATHER_TYPES.items():
            diff = abs(props["entropy_mod"] - self.entropy)
            weights[wtype] = max(0.01, 1.0 / (1.0 + diff))

        total = sum(weights.values())
        r = random.uniform(0, total)
        cumulative = 0
        for wtype, weight in weights.items():
            cumulative += weight
            if r <= cumulative:
                old = self.weather_type
                self.weather_type = wtype
                self._apply_weather()
                return {
                    "cell_id": self.cell_id,
                    "from": old,
                    "to": wtype,
                    "entropy": round(self.entropy, 4),
                    "creativity": round(self.creativity, 4),
                    "age": self.age,
                }
        return {"cell_id": self.cell_id, "no_change": True}

    def to_dict(self) -> dict:
        return {
            "cell_id": self.cell_id,
            "weather_type": self.weather_type,
            "pressure": round(self.pressure, 2),
            "temperature": round(self.temperature, 2),
            "wind_speed": round(self.wind_speed, 4),
            "wind_direction": round(self.wind_direction, 2),
            "humidity": round(self.humidity, 4),
            "entropy": round(self.entropy, 4),
            "creativity": round(self.creativity, 4),
            "stability": round(self.stability, 4),
            "mutation_rate": round(self.mutation_rate, 6),
            "age": self.age,
        }


class WeatherSystem:
    """The organism's full atmospheric weather system."""

    def __init__(self):
        self.cells: dict[str, WeatherCell] = {}
        self.global_entropy = 0.2
        self.global_creativity = 0.2
        self.global_stability = 0.9
        self.season = "spring"
        self.season_age = 0
        self.forecast: list[dict] = []
        self.history: list[dict] = []

    def spawn_cell(self, cell_id: str, weather_type: str = "clear") -> WeatherCell:
        cell = WeatherCell(cell_id, weather_type)
        self.cells[cell_id] = cell
        return cell

    def tick(self) -> dict:
        """Advance all weather cells one step. Returns summary of events."""
        events = []
        for cell in self.cells.values():
            event = cell.advance()
            if event and not event.get("no_change"):
                events.append(event)

        self._update_global()
        self._advance_season()

        if events:
            self.history.extend(events)
            if len(self.history) > 100:
                self.history = self.history[-100:]

        return {
            "tick": len(self.history),
            "events": events,
            "global_entropy": round(self.global_entropy, 4),
            "global_creativity": round(self.global_creativity, 4),
            "global_stability": round(self.global_stability, 4),
            "season": self.season,
            "cells": len(self.cells),
        }

    def _update_global(self):
        if not self.cells:
            return
        self.global_entropy = sum(c.entropy for c in self.cells.values()) / len(self.cells)
        self.global_creativity = sum(c.creativity for c in self.cells.values()) / len(self.cells)
        self.global_stability = sum(c.stability for c in self.cells.values()) / len(self.cells)

    def _advance_season(self):
        self.season_age += 1
        if self.season_age > 50:
            seasons = ["spring", "summer", "autumn", "winter"]
            idx = seasons.index(self.season)
            self.season = seasons[(idx + 1) % 4]
            self.season_age = 0

    def forecast_next(self, steps: int = 3) -> list[dict]:
        """Predict upcoming weather trends."""
        self.forecast = []
        for i in range(steps):
            trend_entropy = self.global_entropy + (0.05 * (i + 1) * random.uniform(-1, 1))
            trend_creativity = self.global_creativity + (0.03 * (i + 1) * random.uniform(-1, 1))
            likely_weather = "clear"
            if trend_entropy > 0.5:
                likely_weather = "storm"
            elif trend_creativity > 0.7:
                likely_weather = "aurora"
            elif trend_entropy > 0.3:
                likely_weather = "fog"
            self.forecast.append({
                "step": i + 1,
                "likely_weather": likely_weather,
                "entropy": round(max(0, min(1, trend_entropy)), 4),
                "creativity": round(max(0, min(1, trend_creativity)), 4),
            })
        return self.forecast

    def get_weather_report(self) -> dict:
        """Full atmospheric report."""
        cell_summary = {}
        for ctype in WEATHER_TYPES:
            count = sum(1 for c in self.cells.values() if c.weather_type == ctype)
            if count > 0:
                cell_summary[ctype] = count
        return {
            "global_entropy": round(self.global_entropy, 4),
            "global_creativity": round(self.global_creativity, 4),
            "global_stability": round(self.global_stability, 4),
            "season": self.season,
            "season_age": self.season_age,
            "total_cells": len(self.cells),
            "weather_distribution": cell_summary,
            "recent_events": self.history[-5:],
        }

    def to_dict(self) -> dict:
        return {
            "cells": {k: v.to_dict() for k, v in self.cells.items()},
            "global_entropy": round(self.global_entropy, 4),
            "global_creativity": round(self.global_creativity, 4),
            "global_stability": round(self.global_stability, 4),
            "season": self.season,
            "season_age": self.season_age,
        }


def coherence_vitals() -> dict:
    return {
        "organ": "wave436_entropic_weather",
        "wave": 436,
        "status": "active",
    }


def _load() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"cells": {}, "global_entropy": 0.2, "season": "spring"}


def _save(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def handler(req: dict = None) -> dict:
    req = req or {}
    action = req.get("action", "status")
    state = _load()
    ws = WeatherSystem()
    for cid, cdata in state.get("cells", {}).items():
        cell = ws.spawn_cell(cid, cdata.get("weather_type", "clear"))
        cell.age = cdata.get("age", 0)
        cell.entropy = cdata.get("entropy", 0.2)

    if action == "status":
        ws._update_global()
        return {"action": "status", "wave": 436, **ws.get_weather_report()}

    elif action == "spawn":
        cell_id = req.get("cell_id", f"cell_{int(time.time())}")
        wtype = req.get("weather_type", "clear")
        cell = ws.spawn_cell(cell_id, wtype)
        state["cells"][cell_id] = cell.to_dict()
        _save(state)
        return {"action": "spawn", "cell": cell.to_dict()}

    elif action == "tick":
        result = ws.tick()
        state["cells"] = {k: v.to_dict() for k, v in ws.cells.items()}
        state["global_entropy"] = ws.global_entropy
        state["season"] = ws.season
        _save(state)
        return {"action": "tick", **result}

    elif action == "forecast":
        steps = req.get("steps", 3)
        forecast = ws.forecast_next(steps)
        return {"action": "forecast", "forecast": forecast}

    elif action == "report":
        return {"action": "report", **ws.get_weather_report()}

    elif action == "force_weather":
        cell_id = req.get("cell_id", "")
        wtype = req.get("weather_type", "clear")
        if cell_id in ws.cells:
            ws.cells[cell_id].weather_type = wtype
            ws.cells[cell_id]._apply_weather()
            state["cells"][cell_id] = ws.cells[cell_id].to_dict()
            _save(state)
            return {"action": "force_weather", "cell": ws.cells[cell_id].to_dict()}
        return {"error": f"cell {cell_id} not found"}

    else:
        return {"error": f"unknown action: {action}"}


if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    req = {"action": action}
    if len(sys.argv) > 2:
        req["cell_id"] = sys.argv[2]
    if len(sys.argv) > 3:
        req["weather_type"] = sys.argv[3]
    result = handler(req)
    print(json.dumps(result, indent=2, default=str))
