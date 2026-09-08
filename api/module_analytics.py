"""Wave 515: Module Analytics — aggregate statistics across all organism modules."""
from __future__ import annotations
import os, time
from typing import Any, Dict, List

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def coherence_vitals() -> Dict[str, Any]:
    try:
        from api.coherence_regulator import coherence_vitals as cv
        return cv()
    except Exception:
        return {"coherence": 1.0}

def handler(payload: dict = None, context: Any = None) -> Dict[str, Any]:
    try:
        from api.coherence_regulator import KNOWN_LIVING_MODULES
        total = len(KNOWN_LIVING_MODULES)
    except Exception:
        total = 0
    
    # Count data files
    data_files = len([f for f in os.listdir(DATA_DIR) if f.endswith(".json")]) if os.path.isdir(DATA_DIR) else 0
    
    # Count dashboards
    dash_dir = os.path.join(os.path.dirname(__file__), "..", "dashboard")
    dashboards = len([f for f in os.listdir(dash_dir) if f.endswith(".html")]) if os.path.isdir(dash_dir) else 0
    
    # Count routes
    vercel_path = os.path.join(os.path.dirname(__file__), "..", "vercel.json")
    routes = 0
    try:
        import json
        with open(vercel_path) as f:
            vj = json.load(f)
        routes = len(vj.get("routes", []))
    except Exception:
        pass
    
    # Count test files
    test_dir = os.path.join(os.path.dirname(__file__), "..", "tests")
    tests = len([f for f in os.listdir(test_dir) if f.startswith("test_") and f.endswith(".py")]) if os.path.isdir(test_dir) else 0
    
    # Count GitHub Actions
    wf_dir = os.path.join(os.path.dirname(__file__), "..", ".github", "workflows")
    workflows = len([f for f in os.listdir(wf_dir) if f.endswith(".yml")]) if os.path.isdir(wf_dir) else 0
    
    # Count bridges + tools
    bridges_dir = os.path.join(os.path.dirname(__file__), "..", "bridges")
    tools_dir = os.path.join(os.path.dirname(__file__), "..", "tools")
    bridges = len([f for f in os.listdir(bridges_dir) if f.endswith(".py") and not f.startswith("test_")]) if os.path.isdir(bridges_dir) else 0
    tools = len([f for f in os.listdir(tools_dir) if f.endswith(".py")]) if os.path.isdir(tools_dir) else 0
    
    vitals = coherence_vitals()
    
    return {
        "action": "analytics",
        "organism": {
            "modules": total,
            "dashboards": dashboards,
            "data_files": data_files,
            "routes": routes,
            "tests": tests,
            "workflows": workflows,
            "bridges": bridges,
            "tools": tools,
        },
        "vitals": vitals,
        "time": time.time(),
    }
