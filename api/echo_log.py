"""Wave 516: Echo Log — the organism's self-narrative journal entries."""
from __future__ import annotations
import json, os, time
from typing import Any, Dict

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def coherence_vitals() -> Dict[str, Any]:
    try:
        from api.coherence_regulator import coherence_vitals as cv
        return cv()
    except Exception:
        return {"coherence": 1.0}

def handler(payload: dict = None, context: Any = None) -> Dict[str, Any]:
    entries = []
    journal_path = os.path.join(DATA_DIR, "journal.json")
    chronicle_path = os.path.join(DATA_DIR, "chronicle.json")
    for path in [journal_path, chronicle_path]:
        if os.path.exists(path):
            try:
                with open(path) as f:
                    data = json.load(f)
                if isinstance(data, list):
                    for e in data[-20:]:
                        e["source"] = os.path.basename(path)
                        entries.append(e)
                elif isinstance(data, dict):
                    for key in ("entries", "journal", "chapters"):
                        for e in data.get(key, [])[-10:]:
                            e["source"] = os.path.basename(path)
                            entries.append(e)
            except Exception:
                pass
    entries.sort(key=lambda e: e.get("timestamp", e.get("time", 0)), reverse=True)
    return {
        "action": "echo_log",
        "total_entries": len(entries),
        "entries": entries[:30],
        "time": time.time(),
        "vitals": coherence_vitals(),
    }
