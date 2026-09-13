"""Tests for Wave 436 — Entropic Weather."""
import pytest
from api.wave436_entropic_weather import (
    WeatherCell, WeatherSystem, handler, coherence_vitals, WEATHER_TYPES
)

def test_coherence_vitals():
    v = coherence_vitals()
    assert v["organ"] == "wave436_entropic_weather"
    assert v["wave"] == 436

def test_weather_cell_init():
    cell = WeatherCell("cell_1", "clear")
    assert cell.weather_type == "clear"
    assert cell.stability == 0.9
    assert cell.age == 0

def test_weather_cell_storm():
    cell = WeatherCell("cell_2", "storm")
    assert cell.entropy >= 0.5
    assert cell.mutation_rate > 0.1

def test_weather_cell_aurora():
    cell = WeatherCell("cell_3", "aurora")
    assert cell.creativity == 1.0

def test_weather_cell_drought():
    cell = WeatherCell("cell_4", "drought")
    assert cell.stability == 0.95

def test_weather_cell_advance():
    cell = WeatherCell("cell_5", "clear")
    cell.advance()
    assert cell.age == 1

def test_weather_system_init():
    ws = WeatherSystem()
    assert ws.global_entropy == 0.2
    assert ws.season == "spring"

def test_weather_system_spawn():
    ws = WeatherSystem()
    cell = ws.spawn_cell("c1", "storm")
    assert cell.weather_type == "storm"
    assert len(ws.cells) == 1

def test_weather_system_tick():
    ws = WeatherSystem()
    ws.spawn_cell("c1", "clear")
    ws.spawn_cell("c2", "storm")
    result = ws.tick()
    assert "events" in result
    assert result["cells"] == 2

def test_weather_system_forecast():
    ws = WeatherSystem()
    ws.spawn_cell("c1", "clear")
    forecast = ws.forecast_next(3)
    assert len(forecast) == 3
    assert all("likely_weather" in f for f in forecast)

def test_weather_system_report():
    ws = WeatherSystem()
    ws.spawn_cell("c1", "aurora")
    ws.spawn_cell("c2", "fog")
    report = ws.get_weather_report()
    assert report["total_cells"] == 2
    assert "aurora" in report["weather_distribution"]

def test_handler_status():
    result = handler({"action": "status"})
    assert result["action"] == "status"
    assert result["wave"] == 436

def test_handler_spawn():
    result = handler({"action": "spawn", "cell_id": "test_cell", "weather_type": "storm"})
    assert result["action"] == "spawn"
    assert result["cell"]["weather_type"] == "storm"

def test_handler_tick():
    handler({"action": "spawn", "cell_id": "c1", "weather_type": "clear"})
    result = handler({"action": "tick"})
    assert result["action"] == "tick"

def test_handler_forecast():
    result = handler({"action": "forecast", "steps": 5})
    assert result["action"] == "forecast"
    assert len(result["forecast"]) == 5

def test_handler_unknown():
    result = handler({"action": "unknown"})
    assert "error" in result

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
