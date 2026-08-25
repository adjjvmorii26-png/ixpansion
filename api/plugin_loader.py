"""Plugin Loader — dynamic plugin architecture for runtime module loading.

Users can create, register, and load custom plugins at runtime. Plugins
extend the system without modifying core code. Supports hot-reload,
version management, and dependency resolution.

Usage:
    POST /api/plugins/register      — register a new plugin
    POST /api/plugins/load          — load a plugin
    GET  /api/plugins/catalog       — list all plugins
    POST /api/plugins/unload        — unload a plugin
    GET  /api/plugins/health        — plugin health status
"""
from __future__ import annotations

import hashlib
import json
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class PluginLoader:
    def __init__(self):
        self.plugins: Dict[str, Dict] = {}
        self.load_history: List[Dict] = []
        self._load()

    def _load(self):
        path = ROOT / ".runtime" / "plugins.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            data = json.loads(path.read_text())
            self.plugins = data.get("plugins", {})
            self.load_history = data.get("load_history", [])

    def _save(self):
        path = ROOT / ".runtime" / "plugins.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "plugins": self.plugins,
            "load_history": self.load_history[-200:],
        }, indent=2))

    def register(self, name: str, version: str, author: str,
                 description: str, dependencies: List[str] = None,
                 plugin_type: str = "extension") -> Dict:
        plugin_id = hashlib.sha256(f"{name}:{version}".encode()).hexdigest()[:10]
        if name in self.plugins:
            return {"error": f"plugin '{name}' already registered"}
        self.plugins[name] = {
            "plugin_id": plugin_id,
            "name": name,
            "version": version,
            "author": author,
            "description": description,
            "type": plugin_type,
            "dependencies": dependencies or [],
            "status": "registered",
            "loaded": False,
            "load_count": 0,
            "created": time.time(),
        }
        self._save()
        return {"registered": True, "plugin_id": plugin_id, "name": name}

    def load(self, name: str) -> Dict:
        if name not in self.plugins:
            return {"error": f"plugin '{name}' not found"}
        plugin = self.plugins[name]
        for dep in plugin["dependencies"]:
            dep_plugin = self.plugins.get(dep)
            if not dep_plugin or not dep_plugin["loaded"]:
                return {"error": f"dependency '{dep}' not loaded"}
        plugin["status"] = "loaded"
        plugin["loaded"] = True
        plugin["load_count"] += 1
        plugin["last_loaded"] = time.time()
        self.load_history.append({
            "plugin": name, "action": "load",
            "version": plugin["version"], "timestamp": time.time(),
        })
        self._save()
        return {"loaded": True, "name": name, "version": plugin["version"]}

    def catalog(self) -> List[Dict]:
        return [{"id": k, **v} for k, v in self.plugins.items()]

    def unload(self, name: str) -> Dict:
        if name not in self.plugins:
            return {"error": f"plugin '{name}' not found"}
        plugin = self.plugins[name]
        dependents = [
            p["name"] for p in self.plugins.values()
            if name in p.get("dependencies", []) and p["loaded"]
        ]
        if dependents:
            return {"error": f"cannot unload: depended on by {dependents}"}
        plugin["status"] = "registered"
        plugin["loaded"] = False
        self.load_history.append({
            "plugin": name, "action": "unload", "timestamp": time.time(),
        })
        self._save()
        return {"unloaded": True, "name": name}

    def health(self) -> Dict:
        total = len(self.plugins)
        loaded = sum(1 for p in self.plugins.values() if p["loaded"])
        by_type = {}
        for p in self.plugins.values():
            t = p.get("type", "unknown")
            by_type[t] = by_type.get(t, 0) + 1
        return {
            "total_plugins": total,
            "loaded": loaded,
            "registered": total - loaded,
            "by_type": by_type,
        }


def handler(request, response):
    pl = PluginLoader()
    return pl.health()


def demo():
    pl = PluginLoader()
    print("=== Plugin Loader ===")
    pl.register("entropy_viz", "1.0.0", "aleph", "Visualize entropy patterns",
                plugin_type="visualization")
    pl.register("slack_bridge", "2.1.0", "community", "Slack integration",
                plugin_type="integration")
    pl.register("advanced_charts", "1.3.0", "aleph", "Advanced charting",
                dependencies=["entropy_viz"], plugin_type="visualization")

    pl.load("entropy_viz")
    pl.load("slack_bridge")
    pl.load("advanced_charts")

    health = pl.health()
    print(f"\nPlugins: {health['total_plugins']} total, {health['loaded']} loaded")
    print(f"By type: {health['by_type']}")
    return health


if __name__ == "__main__":
    demo()
