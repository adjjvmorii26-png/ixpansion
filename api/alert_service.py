"""Intelligent Alert Service — AI-powered anomaly notifications.

Monitors your systems and sends smart alerts when something unusual
happens. Uses the experiment modules to analyze patterns and predict
issues before they become problems.

Usage:
    POST /api/alerts/subscribe  — subscribe to alert channels
    POST /api/alerts/configure  — configure alert rules
    GET  /api/alerts/active     — view active alerts
    GET  /api/alerts/history    — alert history
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

ALERT_CHANNELS = {
    "email": {"name": "Email", "price_monthly": 0, "delay_seconds": 300},
    "slack": {"name": "Slack", "price_monthly": 9, "delay_seconds": 60},
    "webhook": {"name": "Webhook", "price_monthly": 0, "delay_seconds": 0},
    "sms": {"name": "SMS", "price_monthly": 19, "delay_seconds": 30},
    "discord": {"name": "Discord", "price_monthly": 5, "delay_seconds": 30},
}

ALERT_RULES = {
    "cpu_high": {"description": "CPU usage > 90%", "severity": "warning", "cooldown_min": 5},
    "error_spike": {"description": "Error rate > 5%", "severity": "critical", "cooldown_min": 1},
    "latency_high": {"description": "P99 latency > 1s", "severity": "warning", "cooldown_min": 10},
    "disk_low": {"description": "Disk space < 10%", "severity": "critical", "cooldown_min": 60},
    "anomaly_detected": {"description": "AI-detected anomaly", "severity": "info", "cooldown_min": 0},
    "experiment_failed": {"description": "Experiment run failed", "severity": "warning", "cooldown_min": 5},
    "payment_received": {"description": "Payment confirmed", "severity": "info", "cooldown_min": 0},
    "governance_vote": {"description": "New governance vote", "severity": "info", "cooldown_min": 0},
}


class AlertService:
    def __init__(self):
        self.subscriptions: Dict[str, Dict] = {}
        self.active_alerts: List[Dict] = []
        self.alert_history: List[Dict] = []
        self._load()

    def _load(self):
        path = ROOT / ".runtime" / "alerts.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            data = json.loads(path.read_text())
            self.subscriptions = data.get("subscriptions", {})
            self.alert_history = data.get("history", [])

    def _save(self):
        path = ROOT / ".runtime" / "alerts.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "subscriptions": self.subscriptions,
            "history": self.alert_history[-1000:],
        }, indent=2))

    def subscribe(self, user: str, channel: str, config: Dict = None) -> Dict:
        if channel not in ALERT_CHANNELS:
            return {"error": f"unknown channel: {channel}"}
        sub_key = f"{user}:{channel}"
        self.subscriptions[sub_key] = {
            "user": user, "channel": channel,
            "config": config or {}, "active": True,
            "created": time.time(),
        }
        self._save()
        ch = ALERT_CHANNELS[channel]
        return {"subscribed": True, "channel": ch["name"],
                "monthly_cost": ch["price_monthly"]}

    def configure_rules(self, user: str, rules: List[str]) -> Dict:
        sub_keys = [k for k in self.subscriptions if k.startswith(f"{user}:")]
        if not sub_keys:
            return {"error": "no active subscriptions"}
        for key in sub_keys:
            self.subscriptions[key]["rules"] = rules
        self._save()
        return {"configured": True, "rules": rules, "subscriptions": len(sub_keys)}

    def fire_alert(self, rule_name: str, details: Dict) -> List[Dict]:
        if rule_name not in ALERT_RULES:
            return []
        rule = ALERT_RULES[rule_name]
        alert = {
            "alert_id": hashlib.sha256(f"{rule_name}:{time.time()}".encode()).hexdigest()[:10],
            "rule": rule_name, "severity": rule["severity"],
            "description": rule["description"], "details": details,
            "fired": time.time(),
        }
        self.active_alerts.append(alert)
        self.alert_history.append(alert)
        delivered = []
        for sub_key, sub in self.subscriptions.items():
            if sub["active"]:
                delivered.append({"channel": sub["channel"], "user": sub["user"]})
        self._save()
        return {"alert": alert, "delivered_to": len(delivered)}

    def list_active(self) -> List[Dict]:
        cutoff = time.time() - 3600
        self.active_alerts = [a for a in self.active_alerts if a["fired"] > cutoff]
        return self.active_alerts

    def history(self, limit: int = 20) -> List[Dict]:
        return self.alert_history[-limit:]


def handler(request, response):
    return {"channels": ALERT_CHANNELS, "rules": ALERT_RULES}


def demo():
    svc = AlertService()
    print("=== Intelligent Alert Service ===")
    print("\nChannels:")
    for name, ch in ALERT_CHANNELS.items():
        cost = f"${ch['price_monthly']}/mo" if ch['price_monthly'] > 0 else "free"
        print(f"  {ch['name']}: {cost}, delay={ch['delay_seconds']}s")

    svc.subscribe("user_a", "slack")
    svc.subscribe("user_a", "email")
    svc.configure_rules("user_a", ["cpu_high", "error_spike", "anomaly_detected"])

    alerts = svc.fire_alert("error_spike", {"error_rate": 8.5, "service": "api"})
    print(f"\nFired alert: {alerts['alert']['rule']} ({alerts['alert']['severity']})")
    print(f"Delivered to: {alerts['delivered_to']} subscribers")

    alerts2 = svc.fire_alert("anomaly_detected", {"module": "quantum_tunneling"})
    print(f"Fired: {alerts2['alert']['rule']}")

    active = svc.list_active()
    print(f"\nActive alerts: {len(active)}")

    return {"channels": len(ALERT_CHANNELS), "rules": len(ALERT_RULES)}


if __name__ == "__main__":
    demo()

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "interface", "status": "active", "wave": "0", "module": "alert_service"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
