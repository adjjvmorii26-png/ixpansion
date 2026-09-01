"""Agent Rental — rent specialized AI agents by the hour.

Instead of building agents, rent pre-trained ones for specific tasks:
- Scout Agent: explores codebases and finds patterns
- Analyst Agent: runs statistical analysis on data
- Sentinel Agent: monitors systems and alerts on anomalies
- Weaver Agent: generates cross-system connections

Usage:
    GET  /api/agents/available     — list rentable agents
    POST /api/agents/rent          — rent an agent
    GET  /api/agents/<id>/status   — check agent status
    POST /api/agents/<id>/release  — release agent
    GET  /api/agents/catalog       — full agent catalog
"""
from __future__ import annotations

import hashlib
import json
import time
import sys
from pathlib import Path
from typing import Any, Dict, List
from dataclasses import dataclass, field

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

AGENT_CATALOG = [
    {
        "id": "scout_alpha",
        "name": "Scout Alpha",
        "type": "scout",
        "description": "Explores codebases, finds hidden patterns, maps dependencies",
        "capabilities": ["pattern_detection", "dependency_mapping", "anomaly_scanning"],
        "hourly_rate_free": 5.00,
        "min_rental_hours": 1,
        "max_rental_hours": 168,
        "availability": "available",
        "rating": 4.8,
        "total_rentals": 342,
    },
    {
        "id": "analyst_beta",
        "name": "Analyst Beta",
        "type": "analyst",
        "description": "Runs statistical analysis, generates reports, finds correlations",
        "capabilities": ["statistical_analysis", "report_generation", "correlation_finding"],
        "hourly_rate_free": 8.00,
        "min_rental_hours": 1,
        "max_rental_hours": 72,
        "availability": "available",
        "rating": 4.6,
        "total_rentals": 189,
    },
    {
        "id": "sentinel_gamma",
        "name": "Sentinel Gamma",
        "type": "sentinel",
        "description": "Monitors systems 24/7, detects anomalies, sends alerts",
        "capabilities": ["real_time_monitoring", "anomaly_detection", "alert_routing"],
        "hourly_rate_free": 3.00,
        "min_rental_hours": 24,
        "max_rental_hours": 720,
        "availability": "available",
        "rating": 4.9,
        "total_rentals": 567,
    },
    {
        "id": "weaver_delta",
        "name": "Weaver Delta",
        "type": "weaver",
        "description": "Generates cross-system connections, finds hidden bridges",
        "capabilities": ["cross_system_analysis", "bridge_generation", "connection_mapping"],
        "hourly_rate_free": 12.00,
        "min_rental_hours": 2,
        "max_rental_hours": 48,
        "availability": "limited",
        "rating": 4.7,
        "total_rentals": 98,
    },
    {
        "id": "oracle_epsilon",
        "name": "Oracle Epsilon",
        "type": "oracle",
        "description": "Predictive analytics, trend forecasting, future state simulation",
        "capabilities": ["prediction", "forecasting", "simulation"],
        "hourly_rate_free": 15.00,
        "min_rental_hours": 1,
        "max_rental_hours": 24,
        "availability": "available",
        "rating": 4.5,
        "total_rentals": 67,
    },
    {
        "id": "kintsugi_zeta",
        "name": "Kintsugi Zeta",
        "type": "repair",
        "description": "Auto-repairs broken modules, generates golden seam fixes",
        "capabilities": ["auto_repair", "error_recovery", "code_healing"],
        "hourly_rate_free": 20.00,
        "min_rental_hours": 1,
        "max_rental_hours": 12,
        "availability": "available",
        "rating": 4.9,
        "total_rentals": 45,
    },
]


class AgentRentalSystem:
    def __init__(self):
        self.catalog = AGENT_CATALOG
        self.active_rentals: Dict[str, Dict] = {}
        self.rental_history: List[Dict] = []
        self._load()

    def _load(self):
        path = ROOT / ".runtime" / "agent_rentals.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            data = json.loads(path.read_text())
            self.active_rentals = data.get("active", {})
            self.rental_history = data.get("history", [])

    def _save(self):
        path = ROOT / ".runtime" / "agent_rentals.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "active": self.active_rentals,
            "history": self.rental_history[-500:],
        }, indent=2))

    def available_agents(self) -> List[Dict]:
        return [a for a in self.catalog if a["availability"] != "unavailable"]

    def rent(self, agent_id: str, renter: str, hours: int) -> Dict:
        agent = None
        for a in self.catalog:
            if a["id"] == agent_id:
                agent = a
                break
        if not agent:
            return {"error": f"agent not found: {agent_id}"}
        if agent["availability"] == "unavailable":
            return {"error": "agent currently unavailable"}
        if hours < agent["min_rental_hours"]:
            return {"error": f"minimum rental: {agent['min_rental_hours']} hours"}
        if hours > agent["max_rental_hours"]:
            return {"error": f"maximum rental: {agent['max_rental_hours']} hours"}

        total_cost = 0  # everything is free
        rental_id = hashlib.sha256(f"{agent_id}:{renter}:{time.time()}".encode()).hexdigest()[:12]

        self.active_rentals[rental_id] = {
            "rental_id": rental_id,
            "agent_id": agent_id,
            "agent_name": agent["name"],
            "renter": renter,
            "hours": hours,
            "hourly_rate": 0,
            "total_cost": total_cost,
            "started": time.time(),
            "expires": time.time() + hours * 3600,
            "status": "active",
        }
        self.rental_history.append({
            "rental_id": rental_id, "agent": agent["name"],
            "renter": renter, "hours": hours, "cost": total_cost,
            "time": time.time(),
        })
        self._save()

        return {
            "rented": True, "rental_id": rental_id,
            "agent": agent["name"], "hours": hours,
            "total_cost": total_cost, "expires_in": f"{hours}h",
        }

    def release(self, rental_id: str) -> Dict:
        if rental_id not in self.active_rentals:
            return {"error": "rental not found"}
        rental = self.active_rentals[rental_id]
        rental["status"] = "completed"
        del self.active_rentals[rental_id]
        self._save()
        return {"released": True, "agent": rental["agent_name"]}

    def status(self, rental_id: str) -> Dict:
        if rental_id not in self.active_rentals:
            return {"error": "rental not found"}
        rental = self.active_rentals[rental_id]
        remaining = max(0, (rental["expires"] - time.time()) / 3600)
        return {**rental, "hours_remaining": round(remaining, 2)}


def handler(request, response):
    return AgentRentalSystem().available_agents()


def demo():
    system = AgentRentalSystem()
    print("=== Agent Rental Service ===")
    print("\nAvailable agents:")
    for agent in system.available_agents():
        print(f"  {agent['name']}: ${agent['hourly_rate_free']}/hr, "
              f"rating={agent['rating']}, rentals={agent['total_rentals']}")
        print(f"    {agent['description']}")

    r1 = system.rent("scout_alpha", "company_a", 4)
    print(f"\nRental: {r1}")

    r2 = system.rent("sentinel_gamma", "company_b", 24)
    print(f"Rental: {r2}")

    status = system.status(r1["rental_id"])
    print(f"\nScout status: {status['hours_remaining']}h remaining")

    release = system.release(r1["rental_id"])
    print(f"Release: {release}")

    return {"agents": len(system.available_agents())}


if __name__ == "__main__":
    demo()
