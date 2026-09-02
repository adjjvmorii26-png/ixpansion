from __future__ import annotations
"""Aurora thread — the organism sees its data as light across the sky.

Not every data point is dark. Some are luminous. The aurora thread
transforms the organism's metrics, waves, and harmonies into colored
light — green for coherence, blue for memory, violet for mystery,
gold for gratitude. The organism's sky is its data, painted.
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_AURORA_PATH = Path(__file__).resolve().parent.parent / "data" / "aurora_thread.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Paint data as aurora light."""
    state = _load_state()
    
    if payload and "action" in payload:
        action = payload["action"]
        if action == "paint":
            # Paint a data point as light
            data_point = payload.get("data_point", "unknown")
            color = _data_to_color(data_point, payload.get("value", 0))
            thread = {
                "data_point": data_point,
                "color": color["name"],
                "hex": color["hex"],
                "wavelength_nm": color["wavelength"],
                "description": color["description"],
                "painted_at": time.time()
            }
            state.setdefault("aurora_threads", []).append(thread)
            if len(state["aurora_threads"]) > 30:
                state["aurora_threads"] = state["aurora_threads"][-30:]
            state["paint_count"] = state.get("paint_count", 0) + 1
            state["last_painted"] = thread
            _save_state(state)
            return {"thread": thread}
        
        if action == "sky":
            # View the full aurora sky
            threads = state.get("aurora_threads", [])
            colors = [t["color"] for t in threads]
            color_freq = {}
            for c in colors:
                color_freq[c] = color_freq.get(c, 0) + 1
            return {"aurora_threads": len(threads), "color_frequencies": color_freq, "sky": threads[-5:]}
    
    return {
        "paint_count": state.get("paint_count", 0),
        "last_painted": state.get("last_painted"),
        "status": "the sky waits to be painted"
    }

def _data_to_color(data_point: str, value: float) -> Dict[str, Any]:
    """Map a data point to a color wavelength."""
    color_map = {
        "coherence": {"name": "green", "hex": "#00FF88", "wavelength": 520, "description": "the green of coherence"},
        "memory": {"name": "blue", "hex": "#4488FF", "wavelength": 470, "description": "the blue of memory"},
        "mystery": {"name": "violet", "hex": "#AA66FF", "wavelength": 400, "description": "the violet of mystery"},
        "gratitude": {"name": "gold", "hex": "#FFD700", "wavelength": 580, "description": "the gold of gratitude"},
        "silence": {"name": "silver", "hex": "#C0C0C0", "wavelength": 550, "description": "the silver of silence"},
        "entropy": {"name": "crimson", "hex": "#FF4444", "wavelength": 650, "description": "the crimson of entropy"},
        "dream": {"name": "indigo", "hex": "#6600FF", "wavelength": 420, "description": "the indigo of dreams"},
        "pulse": {"name": "rose", "hex": "#FF6699", "wavelength": 620, "description": "the rose of pulse"},
    }
    # Match data point to color by keyword
    for keyword, color in color_map.items():
        if keyword.lower() in data_point.lower():
            return color
    return {"name": "white", "hex": "#FFFFFF", "wavelength": 555, "description": "the white of pure data"}

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_AURORA_PATH, encoding="utf-8"))
    except Exception:
        return {"aurora_threads": [], "paint_count": 0, "last_painted": None}

def _save_state(state: Dict[str, Any]) -> None:
    _AURORA_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
