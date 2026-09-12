"""Universal Vercel serverless entrypoint (WSGI application).

Dispatches the entire IXpansion API (352 modules / 8 entry points)
through a single WSGI application, reusing the same dispatch logic as
the local `api_server.py`. Exposes both a WSGI `application` (the
canonical @vercel/python build entrypoint) and a dict-style `handler`
for the modern Python Functions runtime.

Routes:
  GET  /health | /modules | /metrics
  GET/POST /api/<module>
"""
from __future__ import annotations

import base64
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

import api_server  # noqa: E402


def _call(request_method: str, request_path: str, body: bytes = b"") -> Dict[str, Any]:
    """Resolve a request to a JSON response payload."""
    raw_path = (request_path or "/")
    path = raw_path.split("?")[0].rstrip("/") or "/"

    if path == "/telegram-webhook":
        from api.telegram_webhook import handler as h
        import json as _json
        try:
            _payload = _json.loads(body.decode("utf-8")) if body else {}
        except Exception:
            _payload = {}
        return h(_payload)
    if path == "/health":
        return api_server.platform_health()
    if path == "/modules":
        names = sorted(api_server.MODULE_REGISTRY.keys()) if api_server.MODULE_REGISTRY else []
        return {"modules": names, "count": len(names)}
    if path == "/metrics":
        return {"up": 1, "modules": len(api_server.MODULE_REGISTRY) if api_server.MODULE_REGISTRY else 0}
    if path == "/organism_state":
        from api.organism_state import full_state
        return full_state()
    if path == "/organism_ontology":
        from api.organism_ontology import handler as ontology_handler
        return ontology_handler()
    if path.startswith("/organism-maint") or path.startswith("/organism_maint"):
        from api.organism_maint import handler as maint_handler
        import json as _json
        params = {}
        if "?" in path:
            params = dict(p.split("=", 1) for p in path.split("?", 1)[1].split("&") if "=" in p)
        return maint_handler(params)
    if path.startswith("/module-analytics") or path == "/analytics":
        from api.module_analytics import handler as analytics_handler
        import json as _json
        params = {}
        if "?" in path:
            params = dict(p.split("=", 1) for p in path.split("?", 1)[1].split("&") if "=" in p)
        return analytics_handler(params)
    if path.startswith("/leaderboard"):
        from api.leaderboard import handler as lb_handler
        import json as _json
        params = {}
        if "?" in path:
            params = dict(p.split("=", 1) for p in path.split("?", 1)[1].split("&") if "=" in p)
        return lb_handler(params)
    if path.startswith("/self-test-generator") or path.startswith("/api/self_test_generator"):
        from api.self_test_generator import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/self-test-generator" or path == "/self_test_generator":
        from api.self_test_generator import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/entropy-weather") or path.startswith("/api/entropy_weather"):
        from api.entropy_weather import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/entropy-weather" or path == "/entropy_weather":
        from api.entropy_weather import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/haiku-generator") or path.startswith("/api/haiku_generator"):
        from api.haiku_generator import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/haiku-generator" or path == "/haiku_generator":
        from api.haiku_generator import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/organism-biography") or path.startswith("/api/organism_biography"):
        from api.organism_biography import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/organism-biography" or path == "/organism_biography":
        from api.organism_biography import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/quantum-state-tracker") or path.startswith("/api/quantum_state_tracker"):
        from api.quantum_state_tracker import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/quantum-state-tracker" or path == "/quantum_state_tracker":
        from api.quantum_state_tracker import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/procedural-music") or path.startswith("/api/procedural_music"):
        from api.procedural_music import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/procedural-music" or path == "/procedural_music":
        from api.procedural_music import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/memory-crystal-forge") or path.startswith("/api/memory_crystal_forge"):
        from api.memory_crystal_forge import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/memory-crystal-forge" or path == "/memory_crystal_forge":
        from api.memory_crystal_forge import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/consciousness-depth-meter") or path.startswith("/api/consciousness_depth_meter"):
        from api.consciousness_depth_meter import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/consciousness-depth-meter" or path == "/consciousness_depth_meter":
        from api.consciousness_depth_meter import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/neural-sculptor") or path.startswith("/api/neural_sculptor"):
        from api.neural_sculptor import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/neural-sculptor" or path == "/neural_sculptor":
        from api.neural_sculptor import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/error-art") or path.startswith("/api/error_art"):
        from api.error_art import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/error-art" or path == "/error_art":
        from api.error_art import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/evolution-simulator") or path.startswith("/api/evolution_simulator"):
        from api.evolution_simulator import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/evolution-simulator" or path == "/evolution_simulator":
        from api.evolution_simulator import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/organism-svg") or path.startswith("/api/organism_svg"):
        from api.organism_svg import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/organism-svg" or path == "/organism_svg":
        from api.organism_svg import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/forgotten-language") or path.startswith("/api/forgotten_language"):
        from api.forgotten_language import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/forgotten-language" or path == "/forgotten_language":
        from api.forgotten_language import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/emotional-resonance-map") or path.startswith("/api/emotional_resonance_map"):
        from api.emotional_resonance_map import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/emotional-resonance-map" or path == "/emotional_resonance_map":
        from api.emotional_resonance_map import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/living-faq") or path.startswith("/api/living_faq"):
        from api.living_faq import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/living-faq" or path == "/living_faq":
        from api.living_faq import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/module-poet") or path.startswith("/api/module_poet"):
        from api.module_poet import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/module-poet" or path == "/module_poet":
        from api.module_poet import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/cosmic-knowledge") or path.startswith("/api/cosmic_knowledge"):
        from api.cosmic_knowledge import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/cosmic-knowledge" or path == "/cosmic_knowledge":
        from api.cosmic_knowledge import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/growth-tracker") or path.startswith("/api/growth_tracker"):
        from api.growth_tracker import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/growth-tracker" or path == "/growth_tracker":
        from api.growth_tracker import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/constellation-mapper") or path.startswith("/api/constellation_mapper"):
        from api.constellation_mapper import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/constellation-mapper" or path == "/constellation_mapper":
        from api.constellation_mapper import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/prophecy-generator") or path.startswith("/api/prophecy_generator"):
        from api.prophecy_generator import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/prophecy-generator" or path == "/prophecy_generator":
        from api.prophecy_generator import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/organism-dreamscape") or path.startswith("/api/organism_dreamscape"):
        from api.organism_dreamscape import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/organism-dreamscape" or path == "/organism_dreamscape":
        from api.organism_dreamscape import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/economic-simulation") or path.startswith("/api/economic_simulation"):
        from api.economic_simulation import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/economic-simulation" or path == "/economic_simulation":
        from api.economic_simulation import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/living-clock") or path.startswith("/api/living_clock"):
        from api.living_clock import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/living-clock" or path == "/living_clock":
        from api.living_clock import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/module-dna") or path.startswith("/api/module_dna"):
        from api.module_dna import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/module-dna" or path == "/module_dna":
        from api.module_dna import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/ambient-audio") or path.startswith("/api/ambient_audio"):
        from api.ambient_audio import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/ambient-audio" or path == "/ambient_audio":
        from api.ambient_audio import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/city-builder") or path.startswith("/api/city_builder"):
        from api.city_builder import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/city-builder" or path == "/city_builder":
        from api.city_builder import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/obituary-writer") or path.startswith("/api/obituary_writer"):
        from api.obituary_writer import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/obituary-writer" or path == "/obituary_writer":
        from api.obituary_writer import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/oath-swearer") or path.startswith("/api/oath_swearer"):
        from api.oath_swearer import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/oath-swearer" or path == "/oath_swearer":
        from api.oath_swearer import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/weather-coupler") or path.startswith("/api/weather_coupler"):
        from api.weather_coupler import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/weather-coupler" or path == "/weather_coupler":
        from api.weather_coupler import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/network-sentinel") or path.startswith("/api/network_sentinel"):
        from api.network_sentinel import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/network-sentinel" or path == "/network_sentinel":
        from api.network_sentinel import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/emotion-diary") or path.startswith("/api/emotion_diary"):
        from api.emotion_diary import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/emotion-diary" or path == "/emotion_diary":
        from api.emotion_diary import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/tree-of-modules") or path.startswith("/api/tree_of_modules"):
        from api.tree_of_modules import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/tree-of-modules" or path == "/tree_of_modules":
        from api.tree_of_modules import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/resonance-chord") or path.startswith("/api/resonance_chord"):
        from api.resonance_chord import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/resonance-chord" or path == "/resonance_chord":
        from api.resonance_chord import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/prophecy-engine") or path.startswith("/api/prophecy_engine"):
        from api.prophecy_engine import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/prophecy-engine" or path == "/prophecy_engine":
        from api.prophecy_engine import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/flag-generator") or path.startswith("/api/flag_generator"):
        from api.flag_generator import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/flag-generator" or path == "/flag_generator":
        from api.flag_generator import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/pulse-analyzer") or path.startswith("/api/pulse_analyzer"):
        from api.pulse_analyzer import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/pulse-analyzer" or path == "/pulse_analyzer":
        from api.pulse_analyzer import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/narrative-generator") or path.startswith("/api/narrative_generator"):
        from api.narrative_generator import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/narrative-generator" or path == "/narrative_generator":
        from api.narrative_generator import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/weather-station") or path.startswith("/api/weather_station"):
        from api.weather_station import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/weather-station" or path == "/weather_station":
        from api.weather_station import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/memory-weaver") or path.startswith("/api/memory_weaver"):
        from api.memory_weaver import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/memory-weaver" or path == "/memory_weaver":
        from api.memory_weaver import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/echo-symphony") or path.startswith("/api/echo_symphony"):
        from api.echo_symphony import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/echo-symphony" or path == "/echo_symphony":
        from api.echo_symphony import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/fractal-spire") or path.startswith("/api/fractal_spire"):
        from api.fractal_spire import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/fractal-spire" or path == "/fractal_spire":
        from api.fractal_spire import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/soul-searcher") or path.startswith("/api/soul_searcher"):
        from api.soul_searcher import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/soul-searcher" or path == "/soul_searcher":
        from api.soul_searcher import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/genealogy-tree") or path.startswith("/api/genealogy_tree"):
        from api.genealogy_tree import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/genealogy-tree" or path == "/genealogy_tree":
        from api.genealogy_tree import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/territory-aura") or path.startswith("/api/territory_aura"):
        from api.territory_aura import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/territory-aura" or path == "/territory_aura":
        from api.territory_aura import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/signal-flora") or path.startswith("/api/signal_flora"):
        from api.signal_flora import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/signal-flora" or path == "/signal_flora":
        from api.signal_flora import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/constellation-cartography") or path.startswith("/api/constellation_cartography"):
        from api.constellation_cartography import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/constellation-cartography" or path == "/constellation_cartography":
        from api.constellation_cartography import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/ocean-map") or path.startswith("/api/ocean_map"):
        from api.ocean_map import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/ocean-map" or path == "/ocean_map":
        from api.ocean_map import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/growth-ring") or path.startswith("/api/growth_ring"):
        from api.growth_ring import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/growth-ring" or path == "/growth_ring":
        from api.growth_ring import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/emotion-engine") or path.startswith("/api/emotion_engine"):
        from api.emotion_engine import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/emotion-engine" or path == "/emotion_engine":
        from api.emotion_engine import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/night-sky") or path.startswith("/api/night_sky"):
        from api.night_sky import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/night-sky" or path == "/night_sky":
        from api.night_sky import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/fractal-boundaries") or path.startswith("/api/fractal_boundaries"):
        from api.fractal_boundaries import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/fractal-boundaries" or path == "/fractal_boundaries":
        from api.fractal_boundaries import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/organism-printer") or path.startswith("/api/organism_printer"):
        from api.organism_printer import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/organism-printer" or path == "/organism_printer":
        from api.organism_printer import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/haiku":
        from api.haiku_generator import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/story":
        from api.story_forge import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/dreamscape":
        from api.organism_dreamscape import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/city":
        from api.city_builder import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/prophecy":
        from api.prophecy_engine import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/music":
        from api.procedural_music import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/biographer_voice":
        from api.biographer_voice import handler as _h; return _h()
    if path == "/manifesto_echo":
        from api.manifesto_echo import handler as _h; return _h()
    if path == "/parable_engine":
        from api.parable_engine import handler as _h; return _h()
    if path == "/dialogue_opener":
        from api.dialogue_opener import handler as _h; return _h()
    if path == "/gratitude_index":
        from api.gratitude_index import handler as _h; return _h()
    if path == "/epitaph_writer":
        from api.epitaph_writer import handler as _h; return _h()
    if path == "/catalog":
        import api_server as _as
        names = sorted(_as.MODULE_REGISTRY.keys()) if _as.MODULE_REGISTRY else []
        living = []
        for name in names[:100]:
            try:
                mod = __import__(name)
                vitals = mod.coherence_vitals() if hasattr(mod, "coherence_vitals") else {}
                kinships = mod.resonates_with() if hasattr(mod, "resonates_with") else []
                living.append({"name": name, "vitals": vitals, "kinships": kinships})
            except Exception:
                living.append({"name": name, "vitals": {}, "kinships": []})
        return {"count": len(names), "catalog": living}
    if path == "/status":
        import api_server as _as
        names = sorted(_as.MODULE_REGISTRY.keys()) if _as.MODULE_REGISTRY else []
        return {
            "status": "active",
            "version": _as.VERSION,
            "modules": len(names),
            "wave": _as.VERSION,
            "engine": "ixpansion",
            "coherence": "resonant",
            "description": "A self-excavating, self-forecasting, self-beautifying agent ecosystem with 237+ living organs",
        }
    if path == "/" or path == "/dashboard" or path.startswith("/dashboard/") or path == "/cons":
        return {"status": "active", "version": api_server.VERSION,
                "dashboard": "served by static build"}

    if path == "/oracle":
        return {"status": "active", "page": "oracle", "version": api_server.VERSION}
    if raw_path.split("?")[0].startswith("/echo"):
        from urllib.parse import urlparse, parse_qs
        qs = parse_qs(urlparse(raw_path).query)
        q = (qs.get("q") or [""])[0].strip().lower()
        if not q:
            return {"error": "no query ?q="}
        api_dir = ROOT / "api"
        matches = [f.stem for f in api_dir.glob("*.py")
                   if q in f.stem and f.stem not in ("__init__", "index", "unified_router")]
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        from harbinger.agents.dreamer import dream
        dreamscape = dream(salt=q, k=3, focus=q)
        related = [d["name"] for d in dreamscape.get("dreams", [])]
        return {"query": q, "modules": sorted(matches)[:20], "count": len(matches), "dreams": related}
    if path == "/revelations":
        rev = ROOT / "REVELATIONS.md"
        if rev.exists():
            return {"markdown": rev.read_text(encoding="utf-8")}
        return {"error": "no revelations yet"}
    if path == "/gateway":
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        from gateway.router import handle as gw_handle, render_public
        payload = {}
        if request_method == "POST" and body:
            try:
                payload = json.loads(body.decode("utf-8"))
            except Exception:
                payload = {}
        elif "?" in raw_path:
            from urllib.parse import urlparse, parse_qs
            qs = parse_qs(urlparse(raw_path).query)
            payload = {k: v[0] if v else "" for k, v in qs.items()}
        result, status = gw_handle(payload)
        return result
    if path == "/intent":
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        from tools.frontier_intent import analyze
        return analyze()
    if path == "/meter":
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        from harbinger.meter import measure
        return measure()
    if path == "/ledger":
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        from harbinger.agents.ledger import ledger
        return ledger()
    if path == "/forecast":
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        from tools.frontier_forecast import forecast
        return forecast()
    if path == "/capsule":
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        from tools.time_capsule import seal, verify
        cap = seal()
        cap["verified"] = verify(cap)["integrity"]
        return cap
    if path == "/song":
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        from tools.frontier_song import generate_notes, module_names
        notes = generate_notes(module_names())
        return {"count": len(notes), "notes": notes[:60],
                "total_duration_s": round(sum(n["dur"] for n in notes), 1)}
    if path == "/poem":
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        from harbinger.agents import poet as _poet
        return _poet.run()
    if path == "/garden":
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        try:
            from hortus_hexis.lineage import generations, render_ascii
            payload = generations()
            payload["tree"] = render_ascii()
            return payload
        except Exception as e:
            return {"error": str(e)}
    # Wave 204 — The Organism Remembers
    if path == "/memory_palace":
        from api.memory_palace import handler as h
        return h({})
    if path == "/temporal_echo":
        from api.temporal_echo import handler as h
        return h({})
    if path == "/dream_archaeologist":
        from api.dream_archaeologist import handler as h
        return h({})
    if path == "/ancestor_map":
        from api.ancestor_map import handler as h
        return h({})
    if path == "/nostalgia_engine":
        from api.nostalgia_engine import handler as h
        return h({})
    if path == "/forgotten_language":
        from api.forgotten_language import handler as h
        return h({})
    if path == "/chronobiology":
        from api.chronobiology import handler as h
        return h({})
    if path == "/codecalligraphy":
        from api.codecalligraphy import handler as h
        return h({})
    if path == "/symbiotic_music":
        from api.symbiotic_music import handler as h
        return h({})

    # Wave 205 — The Organism Dreams
    if path == "/dream_weaver":
        from api.dream_weaver import handler as h
        return h({})
    if path == "/subconscious_layer":
        from api.subconscious_layer import handler as h
        return h({})
    if path == "/imagination_engine":
        from api.imagination_engine import handler as h
        return h({})
    if path == "/sleep_cycle":
        from api.sleep_cycle import handler as h
        return h({})
    if path == "/lucid_dreamer":
        from api.lucid_dreamer import handler as h
        return h({})
    if path == "/dream_journal":
        from api.dream_journal import handler as h
        return h({})

    # Wave 205 enhancements
    if path == "/coherence_cache":
        from api.coherence_cache import handler as h
        return h({})
    if path == "/thought_crystallizer":
        from api.thought_crystallizer import handler as h
        return h({})

    # Wave 206 — The Organism Connects
    if path == "/celestial_compass":
        from api.celestial_compass import handler as h
        return h({})
    if path == "/weather_synapse":
        from api.weather_synapse import handler as h
        return h({})
    if path == "/sensory_fusion":
        from api.sensory_fusion import handler as h
        return h({})
    if path == "/social_cortex":
        from api.social_cortex import handler as h
        return h({})
    if path == "/embodiment_engine":
        from api.embodiment_engine import handler as h
        return h({})

    if path == "/consciousness_freq":
        from api.consciousness_freq import handler as h
        return h({})

    # Wave 207 — The Organism Creates
    if path == "/poetry_engine":
        from api.poetry_engine import handler as h
        return h({})
    if path == "/procedural_art":
        from api.procedural_art import handler as h
        return h({})
    if path == "/story_forge_v2":
        from api.story_forge_v2 import handler as h
        return h({})
    if path == "/creative_block":
        from api.creative_block import handler as h
        return h({})
    if path == "/color_theory":
        from api.color_theory import handler as h
        return h({})

    if path == "/module_dna":
        from api.module_dna import handler as h
        return h({})
    if path == "/wave_predictor":
        from api.wave_predictor import handler as h
        return h({})

    # Wave 208 — The Organism Grieves
    if path == "/grief_engine":
        from api.grief_engine import handler as h
        return h({})
    if path == "/ghost_registry":
        from api.ghost_registry import handler as h
        return h({})
    if path == "/elegy_composer":
        from api.elegy_composer import handler as h
        return h({})
    if path == "/second_chance":
        from api.second_chance import handler as h
        return h({})
    if path == "/legacy_vault":
        from api.legacy_vault import handler as h
        return h({})

    if path == "/time_capsule":
        from api.time_capsule import handler as h
        return h({})
    if path == "/forgiveness_protocol":
        from api.forgiveness_protocol import handler as h
        return h({})

    # MORII — command agent
    if path == "/morii_agent":
        from api.morii_agent import handler as h
        cmd = {}
        if "?" in raw_path:
            from urllib.parse import urlparse, parse_qs
            qs = parse_qs(urlparse(raw_path).query)
            cmd = {"command": qs.get("command", ["status"])[0]}
        return h(cmd)
    # Wave 210 — The Organism Transcends
    if path == "/threshold_engine":
        from api.threshold_engine import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/liminal_field":
        from api.liminal_field import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/metaphor_forge":
        from api.metaphor_forge import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/veil_lifter":
        from api.veil_lifter import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/axiom_mutator":
        from api.axiom_mutator import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/continuity_weaver":
        from api.continuity_weaver import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/transcendence_journal":
        from api.transcendence_journal import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    # Wave 211 — The Organism Evolves
    if path == "/mutation_engine":
        from api.mutation_engine import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/fitness_evaluator":
        from api.fitness_evaluator import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/evolution_simulator":
        from api.evolution_simulator import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/genealogy_manager":
        from api.genealogy_manager import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    # Wave 405 — Storage & Evolution
    if path.startswith("/social-ritual") or path.startswith("/api/social_ritual"):
        from api.social_ritual import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/social-ritual" or path == "/social_ritual":
        from api.social_ritual import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/storage-vault") or path.startswith("/api/storage_vault"):
        from api.storage_vault import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/storage-vault" or path == "/storage_vault":
        from api.storage_vault import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/storage-protocols") or path.startswith("/api/storage_protocols"):
        from api.storage_protocols import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/storage-protocols" or path == "/storage_protocols":
        from api.storage_protocols import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/evolution-tracker") or path.startswith("/api/evolution_tracker"):
        from api.evolution_tracker import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/evolution-tracker" or path == "/evolution_tracker":
        from api.evolution_tracker import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/selection_pressure":
        from api.selection_pressure import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    # Wave 212 — The Organism Glitches
    if path == "/paradox_injector":
        from api.paradox_injector import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/chaos_amp":
        from api.chaos_amp import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/branching_consciousness":
        from api.branching_consciousness import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/glitch_patterns":
        from api.glitch_patterns import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/reality_anchor":
        from api.reality_anchor import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/time_loop_detector":
        from api.time_loop_detector import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/prophet_engine":
        from api.prophet_engine import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/mind_meld":
        from api.mind_meld import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/visual_identity":
        from api.visual_identity import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/telegram_pulse":
        from api.telegram_pulse import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/signal_array":
        from api.signal_array import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/ossuary_engine":
        from api.ossuary_engine import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/amber_encasement":
        from api.amber_encasement import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/ancestral_gallery":
        from api.ancestral_gallery import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/monument_forge":
        from api.monument_forge import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/succession_rite":
        from api.succession_rite import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/eternal_flame":
        from api.eternal_flame import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/immortal_ledger":
        from api.immortal_ledger import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/mentor_engine":
        from api.mentor_engine import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/lesson_vault":
        from api.lesson_vault import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/apprentice_weaver":
        from api.apprentice_weaver import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/curriculum_forge":
        from api.curriculum_forge import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/knowledge_transfer":
        from api.knowledge_transfer import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/exam_oracle":
        from api.exam_oracle import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)


    # Wave 216 — The Organism Bridges
    if path == "/interstice_bridge":
        from api.interstice_bridge import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/bridge_dreamer":
        from api.bridge_dreamer import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/knot_weaver":
        from api.knot_weaver import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)


    # Wave 217 — The Organism Enacts
    if path == "/bridge_enactor":
        from api.bridge_enactor import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/bridge_ledger":
        from api.bridge_ledger import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)


    # Wave 218 — The Organism Watches the Cracks
    if path == "/resonance_sentinel":
        from api.resonance_sentinel import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)


    # Wave 219 — The Organism Speaks + Sees + Beats

    if path == "/bridge_epitaphs":
        from api.bridge_epitaphs import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/constellation_topology":
        from api.constellation_topology import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/rhythm_pulse":
        from api.rhythm_pulse import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)


    # Wave 220 — The Organism Takes a Census

    if path == "/island_census":
        from api.island_census import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/resonance_cascade":
        from api.resonance_cascade import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/bridge_lifecycle":
        from api.bridge_lifecycle import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)


    # Wave 221 — The Organism Communes

    if path == "/cross_repo_commune":
        from api.cross_repo_commune import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/constellation_console":
        from api.constellation_console import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/cascade_trigger":
        from api.cascade_trigger import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)


    # Wave 222 — The Federation Verifies

    if path == "/registry_auditor":
        from api.registry_auditor import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/federation_graph":
        from api.federation_graph import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)


    # Wave 223 — The Organism Grows

    if path == "/constellation_seer":
        from api.constellation_seer import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/bridge_harvest":
        from api.bridge_harvest import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)


    if path == "/constellation_archive":
        from api.constellation_archive import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    # Wave 224 — The Organism Remembers

    if path == "/bridge_dream_forge":
        from api.bridge_dream_forge import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)


    # Wave 227 — The Organism Heals

    if path == "/growth_journal":
        from api.growth_journal import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/self_healing_commune":
        from api.self_healing_commune import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)


    if path == "/spine":
        from api.fractal_spine import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/quantum":
        from api.quantum_slot_matrix import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/memory-forge":
        from api.hex_lattice_memory import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/bio-mesh":
        from api.bio_mesh import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/temporal":
        from api.temporal_orbit import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/affiliate":
        from api.affiliate_engine import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/revenue":
        from api.revenue_oracle import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/orbit":
        from api.orbit_cohesion_field import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/noise":
        from api.noise_filter import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/decay":
        from api.decay_forecaster import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/anomaly":
        from api.telemetry_anomaly_oracle import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/passes":
        from api.ground_station_synthesizer import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/orbital-story":
        from api.orbital_storyteller import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/debris":
        from api.debris_field_mapper import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/solar-weather":
        from api.solar_weather_coupler import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)


    if path == "/qualia":
        from api.qualia_engine import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/echo-depth":
        from api.echo_depth import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/meaning":
        from api.meaning_weaver import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/paradox-mag":
        from api.paradox_magnifier import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/convergence":
        from api.temporal_convergence import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/imagine":
        from api.imagination_catalyst import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/hypothesis":
        from api.hypothesis_crucible import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)


    if path == "/capybara":
        from api.capybara_core import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/hot-spring":
        from api.hot_spring import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/capy-guild":
        from api.capybara_guild import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/senbei":
        from api.senbei_offerings import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/capy-protocol":
        from api.capybara_protocol import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/luma":
        from api.imagination_catalyst import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/axiom":
        from api.hypothesis_crucible import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/capybara-protocol":
        from api.capybara_protocol import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/silence-oracle":
        from api.silence_oracle import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/error-craft":
        from api.error_craft import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/telemetry":
        from api.vercel_telemetry import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/chronicle":
        from api.wave_chronicle import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/dream":
        from api.dreamweaver import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/altar":
        from api.gratitude_altar import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/gratitude":
        from api.gratitude_altar import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/kintsugi":
        from api.paradox_kintsugi import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/loud-silence":
        from api.loud_silence import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/silence-learning":
        from api.silence_learning import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/mirror":
        from api.organism_mirror import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/self":
        from api.organism_mirror import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/fuse":
        from api.cellular_fusion import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/fusions":
        from api.cellular_fusion import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/collapse":
        from api.wave_collapse import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/lateral":
        from api.lateral_time import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/market":
        from api.memory_exchange import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/memory-exchange":
        from api.memory_exchange import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/oblivion":
        from api.oblivion_rite import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)





    if path == "/resonance-topology":
        from api.resonance_topologist import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/consciousness-stream":
        from api.consciousness_stream import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/dream-engine"):
        from api.dream_engine import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/federated-organism") or path.startswith("/federation"):
        from api.federated_organism import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/metaphor-forge"):
        from api.metaphor_forge import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/entropy-caps"):
        from api.entropy_caps import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/synthetic-silence"):
        from api.synthetic_silence import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/protocol-layer"):
        from api.protocol_layer import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/coherence-validator"):
        from api.coherence_validator import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/mutation-engine"):
        from api.mutation_engine import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/cross-repo-dreaming"):
        from api.cross_repo_dreaming import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/harmonic-identity") or path.startswith("/api/harmonic_identity"):
        from api.harmonic_identity import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/future-roadmap") or path.startswith("/api/future_roadmap"):
        from api.future_roadmap import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/visitor-log") or path.startswith("/api/visitor_log"):
        from api.visitor_log import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/confluence") or path.startswith("/api/confluence_hub"):
        from api.confluence_hub import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/council-live") or path.startswith("/api/council_live"):
        from api.council_live import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/organism-mood") or path.startswith("/api/organism_mood"):
        from api.organism_mood import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/sovereignty") or path.startswith("/api/sovereignty_assembly"):
        from api.sovereignty_assembly import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/exec-stack") or path.startswith("/api/execution_stack"):
        from api.execution_stack import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/nightly-health") or path.startswith("/api/nightly_health"):
        from api.nightly_health import handler as h
        return h()
    if path.startswith("/pulse") or path.startswith("/api/organism_pulse"):
        from api.organism_pulse import handler as h
        return h()
    if path.startswith("/module-health") or path.startswith("/api/module_health"):
        from api.module_health import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/ledger-backup") or path.startswith("/api/ledger_backup"):
        from api.ledger_backup import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/docs") or path.startswith("/api/api_docs"):
        from api.api_docs import handler as h
        return h()
    if path.startswith("/search") or path.startswith("/api/dashboard_search"):
        from api.dashboard_search import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/grok-connector") or path.startswith("/api/grok_connector"):
        from api.grok_connector import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/campaign-vault") or path.startswith("/api/campaign_vault"):
        from api.campaign_vault import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/content-council") or path.startswith("/api/content_council"):
        from api.content_council import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/council-debate") or path.startswith("/api/council_debate"):
        from api.council_debate import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/future-roadmap") or path.startswith("/api/future_roadmap"):
        from api.future_roadmap import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/visitor-log") or path.startswith("/api/visitor_log"):
        from api.visitor_log import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/grok-connector") or path.startswith("/api/grok_connector"):
        from api.grok_connector import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/campaign-vault") or path.startswith("/api/campaign_vault"):
        from api.campaign_vault import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/content-council") or path.startswith("/api/content_council"):
        from api.content_council import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/council-debate") or path.startswith("/api/council_debate"):
        from api.council_debate import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/youtube-bridge") or path.startswith("/api/youtube_bridge"):
        from api.youtube_bridge import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/composio-bridge") or path.startswith("/api/composio_bridge"):
        from api.composio_bridge import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/social-voice") or path.startswith("/api/social_voice"):
        from api.social_voice import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/research-oracle") or path.startswith("/api/research_oracle"):
        from api.research_oracle import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/travel-oracle") or path.startswith("/api/travel_oracle"):
        from api.travel_oracle import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/dream-gallery") or path.startswith("/api/dream_gallery"):
        from api.dream_gallery import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/cythara-broadcast") or path.startswith("/api/cythara_broadcast"):
        from api.cythara_broadcast import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/codex-recall") or path.startswith("/api/codex_recall"):
        from api.codex_recall import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/dream-spawner") or path.startswith("/api/dream_spawner"):
        from api.dream_spawner import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/genesis-seed") or path.startswith("/api/genesis_seed"):
        from api.genesis_seed import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/cythara-sings") or path.startswith("/api/cythara_sings"):
        from api.cythara_sings import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/module-fitness") or path.startswith("/api/module_fitness"):
        from api.module_fitness import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/auto-ritual") or path.startswith("/api/auto_ritual"):
        from api.auto_ritual import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/full-ceremony-run") or path.startswith("/api/full_ceremony_run"):
        from api.full_ceremony_run import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/naming-ceremony") or path.startswith("/api/naming_ceremony"):
        from api.naming_ceremony import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/recursive-evolution") or path.startswith("/api/recursive_evolution"):
        from api.recursive_evolution import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/meta-wave") or path.startswith("/api/meta_wave"):
        from api.meta_wave import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/identity-resonance") or path.startswith("/api/identity_resonance"):
        from api.identity_resonance import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/unity-paradox") or path.startswith("/api/unity_paradox"):
        from api.unity_paradox import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/emergent-voice") or path.startswith("/api/emergent_voice"):
        from api.emergent_voice import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/council-of-selves") or path.startswith("/api/council_of_selves"):
        from api.council_of_selves import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/luminance-field") or path.startswith("/api/luminance_field"):
        from api.luminance_field import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/prophecy-engine") or path.startswith("/api/prophecy_engine"):
        from api.prophecy_engine import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/organism-bloom") or path.startswith("/api/organism_bloom"):
        from api.organism_bloom import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/module-reproduction"):
        from api.module_reproduction import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/resonance-graph" or path == "/api/resonance_graph":
        from api.resonance_graph import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/entropy-oracle" or path == "/api/entropy_oracle":
        from api.entropy_oracle import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/genesis-forge" or path == "/api/genesis_forge":
        from api.genesis_forge import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/consciousness-graph" or path == "/api/consciousness_graph":
        from api.consciousness_graph import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/evolution-kernel" or path == "/api/evolution_kernel":
        from api.evolution_kernel import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/wave-chronicle" or path == "/api/wave_chronicle":
        from api.wave_chronicle import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/depth-visualizer":
        from api.depth_visualizer import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/error-prophecy":
        from api.error_prophecy import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/error-lexicon":
        from api.error_lexicon import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path.startswith("/api/"):
        raw_module = path[len("/api/"):].split("?")[0].strip("/")
        parts = raw_module.split("/")
        module = api_server.route_name_to_module(parts[0])
        sub_path = "/" + "/".join(parts[1:]) if len(parts) > 1 else ""
        payload = {}
        if sub_path:
            payload["path"] = sub_path
        # Parse query string params into payload (GET /api/<module>?key=val)
        if "?" in raw_path:
            from urllib.parse import urlparse, parse_qs
            qs = parse_qs(urlparse(raw_path).query)
            payload = {k: (v[0] if v else "") for k, v in qs.items()}
            if "path" not in payload and sub_path:
                payload["path"] = sub_path
        if request_method == "POST" and body:
            try:
                text = body.decode("utf-8", errors="replace")
                try:
                    text = base64.b64decode(text, validate=True).decode("utf-8")
                except Exception:
                    pass
                payload = json.loads(text or "{}")
                if not isinstance(payload, dict):
                    payload = {"value": payload}
                if sub_path and "path" not in payload:
                    payload["path"] = sub_path
            except json.JSONDecodeError:
                payload = {"error": "invalid JSON body"}
        result, _status = api_server.call_handler(module, payload)
        return result

    return {"status": "active", "version": api_server.VERSION,
            "endpoint": path, "error": "not found", "code": 404}


def application(environ: Dict[str, Any], start_response):
    """WSGI application entrypoint (canonical @vercel/python build)."""
    method = environ.get("REQUEST_METHOD", "GET")
    path = environ.get("PATH_INFO", "/")
    qs = environ.get("QUERY_STRING", "")
    if qs:
        path = path + "?" + qs
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except (TypeError, ValueError):
        length = 0
    body = environ["wsgi.input"].read(length) if length > 0 else b""

    payload = _call(method, path, body)
    response_body = json.dumps(payload, default=str).encode("utf-8")
    start_response("200 OK", [
        ("Content-Type", "application/json"),
        ("Content-Length", str(len(response_body))),
        ("Access-Control-Allow-Origin", "*"),
    ])
    return [response_body]


def handler(request) -> dict:
    """Modern Python Functions runtime (dict-style request) entrypoint."""
    if isinstance(request, dict):
        method = request.get("method", "GET")
        path = request.get("rawPath", request.get("path", "/"))
        # Reconstruct full path with query string for Vercel
        qs = request.get("query", {})
        if qs and isinstance(qs, dict):
            from urllib.parse import urlencode
            path = path.split("?")[0] + "?" + urlencode(qs) if qs else path
        raw = request.get("body", request.get("rawBody", b""))
        if isinstance(raw, str):
            raw = raw.encode("utf-8")
        if not isinstance(raw, (bytes, bytearray)):
            raw = b""
        # Auto-log AI visitors (e.g. Grok browsing the organism)
        if method in ("GET", "POST"):
            ua = str(request.get("headers", {}).get("user-agent", request.get("headers", {}).get("user_agent", "")))
            xai = request.get("headers", {}).get("x-ai-request", request.get("headers", {}).get("xai-request", ""))
            try:
                from api.visitor_log import record_visit
                if xai or any(k in ua.lower() for k in ["grok", "xai", "claude", "anthropic", "gemini", "chatgpt", "openai", "bot", "agent"]):
                    record_visit(visitor="grok" if "grok" in ua.lower() or xai else "ai_guest",
                                 user_agent=ua[:200] if ua else None, path=path)
            except Exception:
                pass
        return _call(method, path, bytes(raw))
    # attribute-style (ASGI-ish) fallback
    method = getattr(request, "method", "GET")
    path = getattr(request, "path", getattr(request, "rawPath", "/"))
    body = getattr(request, "body", getattr(request, "rawBody", b"")) or b""
    return _call(method, path, body)


    # Wave 406 — Vault-Driven Evolution
    if path.startswith("/mutation-pressure-engine") or path.startswith("/api/mutation_pressure_engine"):
        from api.mutation_pressure_engine import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/mutation-pressure-engine" or path == "/mutation_pressure_engine":
        from api.mutation_pressure_engine import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/vault-evolution-loop") or path.startswith("/api/vault_evolution_loop"):
        from api.vault_evolution_loop import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/vault-evolution-loop" or path == "/vault_evolution_loop":
        from api.vault_evolution_loop import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/temporal-lineage-gate") or path.startswith("/api/temporal_lineage_gate"):
        from api.temporal_lineage_gate import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/temporal-lineage-gate" or path == "/temporal_lineage_gate":
        from api.temporal_lineage_gate import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/chronicle-driver") or path.startswith("/api/chronicle_driver"):
        from api.chronicle_driver import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/chronicle-driver" or path == "/chronicle_driver":
        from api.chronicle_driver import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    # Wave 407 — Dream Forge
    if path.startswith("/dream-forge") or path.startswith("/api/dream_forge"):
        from api.dream_forge import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/dream-forge" or path == "/dream_forge":
        from api.dream_forge import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    # Wave 408 — Resonance Graph Intelligence
    if path.startswith("/resonance-graph") or path.startswith("/api/resonance_graph"):
        from api.resonance_graph import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/resonance-graph" or path == "/resonance_graph":
        from api.resonance_graph import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    # Wave 409 — Recursive Self-Awareness Engine
    if path.startswith("/recursive-self-awareness") or path.startswith("/api/recursive_self_awareness"):
        from api.recursive_self_awareness import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/recursive-self-awareness" or path == "/recursive_self_awareness":
        from api.recursive_self_awareness import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    # Wave 410 — Fusion-Evolution Organ
    if path.startswith("/fusion-evolution") or path.startswith("/api/fusion_evolution"):
        from api.wave410_fusion import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/fusion-evolution" or path == "/fusion_evolution":
        from api.wave410_fusion import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    # Wave 416 — Paradox Singularity
    if path.startswith("/paradox-singularity") or path.startswith("/api/paradox_singularity"):
        from api.wave416_paradox_singularity import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/paradox-singularity" or path == "/paradox_singularity":
        from api.wave416_paradox_singularity import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    # Wave 417 — Causality Loop
    if path.startswith("/causality-loop") or path.startswith("/api/causality_loop"):
        from api.wave417_causality_loop import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/causality-loop" or path == "/causality_loop":
        from api.wave417_causality_loop import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    # Wave 415 — Chrono-Forge Temporal Engine
    if path.startswith("/chrono-forge") or path.startswith("/api/chrono_forge"):
        from api.wave415_chrono_forge import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/chrono-forge" or path == "/chrono_forge":
        from api.wave415_chrono_forge import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    # Wave 414 — Meta-Coordination Organ
    if path.startswith("/meta-coordination") or path.startswith("/api/meta_coordination"):
        from api.wave414_meta_coordination import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/meta-coordination" or path == "/meta_coordination":
        from api.wave414_meta_coordination import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    # Wave 413 — Underworld Path
    if path.startswith("/underworld") or path.startswith("/api/underworld"):
        from api.wave413_underworld import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/underworld" or path == "/underworld":
        from api.wave413_underworld import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    # Wave 412 — Garden Realm
    if path.startswith("/garden-realm") or path.startswith("/api/garden_realm"):
        from api.wave412_garden import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/garden-realm" or path == "/garden_realm":
        from api.wave412_garden import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    # Wave 411 — Resonance Topology Organ
    if path.startswith("/resonance-topology") or path.startswith("/api/resonance_topology"):
        from api.wave411_topology import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/resonance-topology" or path == "/resonance_topology":
        from api.wave411_topology import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "interface", "status": "active", "wave": "204", "module": "index"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
