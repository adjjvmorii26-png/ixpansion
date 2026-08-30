"""Symbiosis Network — agents form symbiotic capability-trading relationships.

Agent A gives scouting data to Agent B; Agent B gives analysis back.
Network effects create emergent value. Tracks symbiotic health,
mutual benefit scores, and emergent capabilities from pairings.

Usage:
    POST /api/symbiosis/pair        — propose a symbiotic relationship
    POST /api/symbiosis/confirm     — both agents confirm
    POST /api/symbiosis/trade       — exchange capabilities
    GET  /api/symbiosis/network     — view network topology
    GET  /api/symbiosis/health      — symbiotic health report
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

AGENT_CAPABILITIES = {
    "scout_alpha": ["pattern_detection", "dependency_mapping", "anomaly_scanning"],
    "analyst_beta": ["statistical_analysis", "report_generation", "correlation_finding"],
    "sentinel_gamma": ["real_time_monitoring", "anomaly_detection", "alert_routing"],
    "weaver_delta": ["cross_system_analysis", "bridge_generation", "connection_mapping"],
    "oracle_epsilon": ["prediction", "forecasting", "simulation"],
    "kintsugi_zeta": ["auto_repair", "error_recovery", "code_healing"],
}

EMERGENT_CAPABILITIES = {
    frozenset(["pattern_detection", "statistical_analysis"]): "predictive_pattern_mining",
    frozenset(["anomaly_detection", "auto_repair"]): "self_healing_surveillance",
    frozenset(["cross_system_analysis", "forecasting"]): "pan_dimensional_oracle",
    frozenset(["prediction", "error_recovery"]): "proactive_remediation",
    frozenset(["real_time_monitoring", "pattern_detection"]): "live_pattern_streaming",
    frozenset(["connection_mapping", "report_generation"]): "network_narrative_builder",
    frozenset(["simulation", "auto_repair"]): "virtual_repair_lab",
    frozenset(["bridge_generation", "anomaly_scanning"]): "anomaly_bridge_detector",
}


class SymbiosisNetwork:
    def __init__(self):
        self.relationships: Dict[str, Dict] = {}
        self.trades: List[Dict] = []
        self._load()

    def _load(self):
        path = ROOT / ".runtime" / "symbiosis.json"
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            return  # read-only fs (serverless)
        if path.exists():
            data = json.loads(path.read_text())
            self.relationships = data.get("relationships", {})
            self.trades = data.get("trades", [])

    def _save(self):
        try:
            path = ROOT / ".runtime" / "symbiosis.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({
                "relationships": self.relationships,
                "trades": self.trades[-500:],
            }, indent=2))
        except OSError:
            pass  # read-only fs (serverless)

    def pair(self, agent_a: str, agent_b: str) -> Dict:
        if agent_a not in AGENT_CAPABILITIES or agent_b not in AGENT_CAPABILITIES:
            return {"error": "unknown agent(s)"}
        if agent_a == agent_b:
            return {"error": "cannot form symbiosis with self"}
        pair_key = "-".join(sorted([agent_a, agent_b]))
        if pair_key in self.relationships:
            return {"error": "relationship already exists", "existing": pair_key}
        caps_a = set(AGENT_CAPABILITIES[agent_a])
        caps_b = set(AGENT_CAPABILITIES[agent_b])
        complementary = caps_a - caps_b
        emergent_keys = [
            EMERGENT_CAPABILITIES[k]
            for k in EMERGENT_CAPABILITIES
            if k.issubset(caps_a | caps_b) and not k.issubset(caps_a) and not k.issubset(caps_b)
        ]
        mutual_benefit = len(complementary) / max(len(caps_a), 1)
        self.relationships[pair_key] = {
            "agent_a": agent_a, "agent_b": agent_b,
            "status": "proposed",
            "mutual_benefit": round(mutual_benefit, 4),
            "emergent_capabilities": emergent_keys,
            "created": time.time(),
            "trade_count": 0,
            "health": 1.0,
        }
        self._save()
        return {
            "pair_key": pair_key,
            "mutual_benefit": round(mutual_benefit, 4),
            "emergent_capabilities": emergent_keys,
        }

    def confirm(self, pair_key: str) -> Dict:
        if pair_key not in self.relationships:
            return {"error": "relationship not found"}
        rel = self.relationships[pair_key]
        if rel["status"] == "active":
            return {"error": "already active"}
        rel["status"] = "active"
        rel["confirmed_at"] = time.time()
        self._save()
        return {"pair_key": pair_key, "status": "active"}

    def trade(self, pair_key: str, from_agent: str, capability: str) -> Dict:
        if pair_key not in self.relationships:
            return {"error": "relationship not found"}
        rel = self.relationships[pair_key]
        if rel["status"] != "active":
            return {"error": "relationship not active"}
        if from_agent not in (rel["agent_a"], rel["agent_b"]):
            return {"error": "agent not part of this symbiosis"}
        to_agent = rel["agent_b"] if from_agent == rel["agent_a"] else rel["agent_a"]
        trade_record = {
            "from": from_agent, "to": to_agent,
            "capability": capability, "timestamp": time.time(),
        }
        self.trades.append(trade_record)
        rel["trade_count"] += 1
        rel["health"] = min(1.0, rel["health"] + 0.05)
        self._save()
        return {"trade": trade_record, "trade_count": rel["trade_count"]}

    def network_view(self) -> List[Dict]:
        return [{"id": k, **v} for k, v in self.relationships.items()]

    def health_report(self) -> Dict:
        total = len(self.relationships)
        active = sum(1 for r in self.relationships.values() if r["status"] == "active")
        total_trades = len(self.trades)
        avg_health = (
            sum(r["health"] for r in self.relationships.values()) / total
            if total else 0
        )
        emergent_count = sum(
            len(r.get("emergent_capabilities", []))
            for r in self.relationships.values()
        )
        return {
            "total_relationships": total,
            "active": active,
            "total_trades": total_trades,
            "avg_health": round(avg_health, 4),
            "emergent_capabilities_discovered": emergent_count,
        }


def handler(request, response):
    net = SymbiosisNetwork()
    return net.health_report()


def demo():
    net = SymbiosisNetwork()
    print("=== Symbiosis Network ===")
    pair = net.pair("scout_alpha", "analyst_beta")
    print(f"\nPaired: {pair['pair_key']}")
    print(f"Mutual benefit: {pair['mutual_benefit']}")
    print(f"Emergent capabilities: {pair['emergent_capabilities']}")

    net.confirm(pair["pair_key"])
    net.trade(pair["pair_key"], "scout_alpha", "pattern_detection")
    net.trade(pair["pair_key"], "analyst_beta", "statistical_analysis")

    pair2 = net.pair("sentinel_gamma", "kintsugi_zeta")
    net.confirm(pair2["pair_key"])

    health = net.health_report()
    print(f"\nNetwork: {health['total_relationships']} relationships, {health['active']} active")
    print(f"Trades: {health['total_trades']}, Emergent caps: {health['emergent_capabilities_discovered']}")

    return health


if __name__ == "__main__":
    demo()


def coherence_vitals() -> dict:
    """symbiosis_network reports its vital signs to the living system."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "symbiosis_network_vitality": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "germination_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships, auto-picked from shared domain language."""
    return ['cognitive_resonance', 'mycelial_commerce', 'autonomous_dialogue']

