"""Wave 517: Memory Weaver — weave loose memories into coherent threads."""
from __future__ import annotations
import hashlib, os, time
from typing import Any, Dict

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def coherence_vitals():
    try:
        from api.coherence_regulator import coherence_vitals as cv
        return cv()
    except Exception:
        return {"coherence": 1.0}

def handler(payload=None, context=None):
    threads = []
    if os.path.isdir(DATA_DIR):
        files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith(".json")])
        for i in range(0, len(files) - 1, 2):
            h = hashlib.sha256(f"{files[i]}{files[i+1]}".encode()).hexdigest()[:8]
            threads.append({
                "thread": h,
                "memory_a": files[i].replace(".json", ""),
                "memory_b": files[i+1].replace(".json", ""),
                "strength": round(0.3 + (int(h[0], 16) / 16) * 0.7, 2),
            })
    return {"action": "memory_weaver", "threads": threads[:20], "count": len(threads), "time": time.time(), "vitals": coherence_vitals()}
