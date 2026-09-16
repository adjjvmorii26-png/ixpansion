"""Wave 754 — mycelial_weather.

The organism's climate: nutrient scarcity, signal currents, and forecasts.
Mycelial weather decides where the ecosystem has room to grow (nutrient-rich)
and where mutation pressure accumulates (nutrient-scarce domains).
"""
from __future__ import annotations

import datetime
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "wave754_mycelial_weather.json"
WAVE = 754
NAME = "mycelial_weather"

_BIOME_WORDS = {
    "dream": "dream", "lucid": "dream", "mood": "dream",
    "memory": "memory", "echo": "memory", "archive": "memory",
    "quantum": "quantum", "paradox": "quantum",
    "mesh": "mesh", "node": "mesh", "relay": "mesh",
    "gene": "gene", "dna": "gene", "splice": "gene", "seed": "gene",
    "oracle": "oracle", "entropy": "oracle", "observer": "oracle",
    "ritual": "ritual", "ceremony": "ritual", "chrono": "ritual",
    "weather": "weather", "climate": "weather", "tide": "weather",
    "grail": "grail", "myth": "grail", "lore": "grail",
}


def _load() -> dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except Exception:
            pass
    return {"wave": WAVE, "name": NAME, "forecasts": [], "status": "seed"}


def _save(state: dict) -> None:
    DATA_FILE.write_text(json.dumps(state, indent=2))


def _module_names() -> list:
    names = []
    for p in (ROOT / "api").glob("wave*.py"):
        m = re.match(r"wave\d+_(.+)\.py", p.name)
        if m:
            names.append(m.group(1))
    return sorted(names)


def _nutrient_map(names: list) -> Dict[str, dict]:
    counts: Counter = Counter()
    for n in names:
        biome = next((b for word, b in _BIOME_WORDS.items() if word in n), "wild")
        counts[biome] += 1
    total = max(len(names), 1)
    nutrients = {}
    for biome, count in counts.items():
        share = count / total
        nutrients[biome] = {
            "organs": count,
            "share": round(share, 3),
            "grade": "fertile" if share > 0.12 else ("temperate" if share > 0.05 else "scarce"),
        }
    return nutrients


def _seed_weather() -> Dict[str, Any]:
    return {
        "entropy": 0.47,
        "signal_decay": 0.21,
        "nutrient_pressure": 0.38,
        "phase": "growing",
        "advisory": "currents steady; scarce biomes invite new organs",
    }


def _forecast(days: int = 5, nutrient_map: Dict[str, dict] = None) -> Dict[str, Any]:
    base = _seed_weather()
    scarce = sorted((b for b, m in (nutrient_map or {}).items() if m["grade"] == "scarce"))
    series = []
    for d in range(1, days + 1):
        drift = round(0.03 * d, 3)
        series.append({
            "day": d,
            "entropy": round(min(0.95, base["entropy"] + drift), 3),
            "signal_decay": round(min(0.9, base["signal_decay"] + 0.02 * d), 3),
            "mood": "lucid" if d < 3 else "liminal",
        })
    advisory = f"mutation pressure building in scarce biomes: {', '.join(scarce) or 'none'}; plant new organs there"
    return {"base": base, "series": series, "advisory": advisory, "days": days}


def handler(req: dict) -> dict:
    action = req.get("action", "status")
    state = _load()
    names = _module_names()
    nutrients = _nutrient_map(names)

    if action == "status":
        state["last_check"] = datetime.datetime.now(datetime.UTC).isoformat()
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "status", "ok": True,
                "organs": len(names), "biomes": nutrients, "forecasts": len(state.get("forecasts", []))}

    if action == "ping":
        return {"wave": WAVE, "name": NAME, "action": "ping", "ok": True, "alive": True}

    if action == "forecast":
        days = min(int(req.get("days", 5)), 30)
        fc = _forecast(days, nutrients)
        state.setdefault("forecasts", []).append({"at": datetime.datetime.now(datetime.UTC).isoformat(), **fc["base"]})
        state["forecasts"] = state["forecasts"][-10:]
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "forecast", "ok": True, **fc}

    if action == "currents":
        scarce = [b for b, m in nutrients.items() if m["grade"] == "scarce"]
        fertile = [b for b, m in nutrients.items() if m["grade"] == "fertile"]
        flavor = "spring-tide (expansion)" if len(scarce) >= 2 else "estuary (reshuffle)"
        return {"wave": WAVE, "name": NAME, "action": "currents", "ok": True,
                "organs": len(names), "fertile": fertile, "scarce": scarce, "flavor": flavor}

    if action == "nutrients":
        return {"wave": WAVE, "name": NAME, "action": "nutrients", "ok": True, "biomes": nutrients,
                "coverage": round(len(nutrients) / max(len(_BIOME_WORDS) // 2, 1), 2)}

    return {"wave": WAVE, "name": NAME, "action": action, "ok": False, "error": "unknown_action"}


def coherence_vitals() -> dict:
    state = _load()
    return {"wave": WAVE, "name": NAME, "layer": "organ", "status": "active",
            "resonance": 0.61, "forecasts": len(state.get("forecasts", [])),
            "module_health": {"value": 0.78, "setpoint": 0.75, "weight": 1.0}}


def resonates_with() -> list:
    return ["resonance_braid", "evolution_kernel", "gene_splicer"]
