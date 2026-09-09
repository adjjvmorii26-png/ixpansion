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


class ModuleAnalytics:
    """Tracks per-module call analytics: frequency, latency, success."""

    def __init__(self):
        self._records = []
        self._modules = {}

    def record(self, module: str, action: str, latency: float, success: bool) -> Dict:
        entry = {"module": module, "action": action, "latency": latency,
                 "success": success, "timestamp": time.time()}
        self._records.append(entry)
        if module not in self._modules:
            self._modules[module] = {"calls": 0, "successes": 0, "failures": 0,
                                     "total_latency": 0.0, "actions": {}}
        m = self._modules[module]
        m["calls"] += 1
        m["successes"] += 1 if success else 0
        m["failures"] += 0 if success else 1
        m["total_latency"] += latency
        m["actions"][action] = m["actions"].get(action, 0) + 1
        return entry

    def module_report(self, module: str) -> Dict:
        m = self._modules.get(module, {})
        return {"module": module, "calls": m.get("calls", 0),
                "successes": m.get("successes", 0), "failures": m.get("failures", 0),
                "avg_latency": round(m.get("total_latency", 0) / max(m.get("calls", 1), 1), 6)}

    def top_modules(self, metric: str = "calls", limit: int = 5) -> list:
        rows = []
        for name, m in self._modules.items():
            rows.append({"name": name, "calls": m["calls"], "successes": m["successes"],
                         "failures": m["failures"], "avg_latency": round(m["total_latency"] / max(m["calls"], 1), 6)})
        rows.sort(key=lambda r: r.get(metric, 0), reverse=True)
        return rows[:limit]

    def system_health(self) -> Dict:
        total = len(self._records)
        ok = sum(1 for r in self._records if r["success"])
        return {"total_calls": total, "success_rate": round(ok / max(total, 1), 3),
                "active_modules": len(self._modules)}
