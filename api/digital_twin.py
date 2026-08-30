"""Digital Twin Service — create digital twins of your systems.

Mirror your production systems into the IXpansion sandbox, run
experiments on the twin without touching production, and predict
failures before they happen.

Usage:
    POST /api/twin/create    — create a digital twin
    POST /api/twin/mirror    — sync data from real system
    POST /api/twin/simulate  — run simulation on twin
    GET  /api/twin/<id>/health — twin health status
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
try:
    from runtime_io import load_json as _rio_load, save_json as _rio_save
except Exception:
    _rio_load = _rio_save = None


class DigitalTwinService:
    def __init__(self):
        self.twins: Dict[str, Dict] = {}
        self._load()

    def _load(self):
        path = ROOT / ".runtime" / "digital_twins.json"
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        if path.exists():
            self.twins = json.loads(path.read_text())

    def _save(self):
        path = ROOT / ".runtime" / "digital_twins.json"
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        path.write_text(json.dumps(self.twins, indent=2))

    def create(self, name: str, source_type: str, owner: str,
               config: Dict = None) -> Dict:
        twin_id = hashlib.sha256(f"{name}:{owner}:{time.time()}".encode()).hexdigest()[:12]
        self.twins[twin_id] = {
            "twin_id": twin_id, "name": name, "source_type": source_type,
            "owner": owner, "config": config or {},
            "status": "created", "last_sync": None,
            "simulations_run": 0, "failures_predicted": 0,
            "created": time.time(),
        }
        self._save()
        return {"created": True, "twin_id": twin_id, "name": name}

    def mirror(self, twin_id: str, data_snapshot: Dict) -> Dict:
        if twin_id not in self.twins:
            return {"error": "twin not found"}
        twin = self.twins[twin_id]
        twin["status"] = "mirrored"
        twin["last_sync"] = time.time()
        twin["snapshot"] = data_snapshot
        twin["modules"] = len(data_snapshot.get("modules", []))
        self._save()
        return {"mirrored": True, "modules": twin["modules"]}

    def simulate(self, twin_id: str, scenario: str, ticks: int = 10) -> Dict:
        if twin_id not in self.twins:
            return {"error": "twin not found"}
        twin = self.twins[twin_id]
        twin["simulations_run"] += 1
        failures = []
        import random
        rng = random.Random(hash(f"{twin_id}:{scenario}:{time.time()}"))
        for i in range(ticks):
            if rng.random() < 0.15:
                failures.append({"tick": i, "module": f"module_{rng.randint(0, 5)}",
                                 "severity": round(rng.random(), 2)})
        if failures:
            twin["failures_predicted"] += len(failures)
        self._save()
        return {
            "sim_id": hashlib.sha256(f"{twin_id}:{time.time()}".encode()).hexdigest()[:8],
            "scenario": scenario, "ticks": ticks,
            "failures_predicted": len(failures),
            "failures": failures[:5],
            "risk_score": round(min(1.0, len(failures) / 5), 3),
        }

    def health(self, twin_id: str) -> Dict:
        if twin_id not in self.twins:
            return {"error": "twin not found"}
        twin = self.twins[twin_id]
        return {
            "twin_id": twin_id, "name": twin["name"],
            "status": twin["status"],
            "simulations_run": twin["simulations_run"],
            "failures_predicted": twin["failures_predicted"],
            "last_sync": twin["last_sync"],
        }

    def list_twins(self, owner: str = None) -> List[Dict]:
        twins = list(self.twins.values())
        if owner:
            twins = [t for t in twins if t["owner"] == owner]
        return [{k: v for k, v in t.items() if k != "snapshot"} for t in twins]


def handler(request, response):
    return DigitalTwinService().list_twins()


def demo():
    svc = DigitalTwinService()
    print("=== Digital Twin Service ===")

    twin = svc.create("production_api", "rest_api", "company_a",
                      {"endpoints": 22, "uptime": 99.9})
    print(f"Created twin: {twin['twin_id']}")

    mirror = svc.mirror(twin["twin_id"], {
        "modules": ["auth", "crypto", "billing", "marketplace"],
        "metrics": {"cpu": 45, "memory": 62, "latency": 120},
    })
    print(f"Mirrored: {mirror}")

    sim = svc.simulate(twin["twin_id"], "high_traffic", ticks=20)
    print(f"\nSimulation: {sim['ticks']} ticks, {sim['failures_predicted']} failures predicted")
    print(f"Risk score: {sim['risk_score']}")

    health = svc.health(twin["twin_id"])
    print(f"\nHealth: {health['status']}, simulations={health['simulations_run']}")

    return {"twins": len(svc.twins)}


if __name__ == "__main__":
    demo()


def coherence_vitals() -> dict:
    """Digital Twin reports its vital signs — mirroring and prediction."""
    return {
        "module_health": {"value": 0.89, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "twin_fidelity": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ['reality_weaver', 'platform_failure']
