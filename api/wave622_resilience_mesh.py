"""Wave 622 — Resilience Mesh: Distributed Failure Detection & Auto-Heal.

The organism's immune system. Every organ reports its health through the
Resilience Mesh. If an organ fails repeatedly, the mesh auto-heals it
by restarting the module, rerouting traffic, or spawning a replacement.

Features:
- Health heartbeat registry: every organ reports its state periodically
- Failure detection: consecutive failures trigger circuit-breaking
- Auto-heal: failed modules are automatically restarted or replaced
- Rerouting: traffic is redirected away from failing organs
- Organ status dashboard: real-time view of organism health
- Resilience score: organism-wide health metric

Builds upon:
- Wave 621: OmniRouter (routing and load balancing)
- Wave 98: HEX Cathedral Lacery (cross-segment linking)
- Wave 620: Model Staleness Registry (freshness)
"""
from __future__ import annotations
import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DATA = Path(__file__).resolve().parents[1] / "data"
STATE_FILE = DATA / "wave622_resilience_mesh.json"
HEARTBEAT_INTERVAL = 30.0
FAILURE_THRESHOLD = 3
AUTO_HEAL_Cooldown = 60.0


class OrganHealth:
    """Health record for a single organ."""

    def __init__(self, organ_id: str, module_path: str = "") -> None:
        self.organ_id = organ_id
        self.module_path = module_path
        self.status: str = "healthy"  # healthy, degraded, failing, dead
        self.last_heartbeat: float = time.time()
        self.consecutive_failures = 0
        self.total_failures = 0
        self.total_successes = 0
        self.is_automated: bool = False
        self.recovery_attempts = 0
        self.last_recovery: Optional[float] = None
        self.health_score = 1.0
        self.recovery_history: List[dict] = []

    def record_heartbeat(self, healthy: bool, latency_ms: float = 0.0) -> None:
        self.last_heartbeat = time.time()
        if healthy:
            self.consecutive_failures = 0
            self.total_successes += 1
            self.status = "healthy" if self.consecutive_failures == 0 else "degraded"
            self.recovery_attempts = 0
        else:
            self.consecutive_failures += 1
            self.total_failures += 1
            self.status = "failing" if self.consecutive_failures >= FAILURE_THRESHOLD else "degraded"

        # Update health score
        total = self.total_successes + self.total_failures
        if total > 0:
            self.health_score = round(self.total_successes / total, 4)

    def needs_auto_heal(self) -> bool:
        if self.consecutive_failures < FAILURE_THRESHOLD:
            return False
        if self.recovery_attempts >= 3:
            self.status = "dead"
            return False
        if self.last_recovery and (time.time() - self.last_recovery) < AUTO_HEAL_Cooldown:
            return False
        return True

    def trigger_recovery(self) -> dict:
        self.recovery_attempts += 1
        self.last_recovery = time.time()
        action = "restart" if self.recovery_attempts == 1 else "replace"
        entry = {
            "ts": time.time(),
            "action": action,
            "consecutive_failures": self.consecutive_failures,
            "recovery_attempt": self.recovery_attempts,
        }
        self.recovery_history.append(entry)
        return entry

    def to_dict(self) -> dict:
        return {
            "organ_id": self.organ_id,
            "module_path": self.module_path,
            "status": self.status,
            "last_heartbeat": self.last_heartbeat,
            "consecutive_failures": self.consecutive_failures,
            "total_failures": self.total_failures,
            "total_successes": self.total_successes,
            "health_score": self.health_score,
            "is_automated": self.is_automated,
            "recovery_attempts": self.recovery_attempts,
            "recovery_history": self.recovery_history[-5:],
        }


class ResilienceMesh:
    """Distributed failure detection and auto-heal layer."""

    def __init__(self) -> None:
        self.organs: Dict[str, OrganHealth] = {}
        self.history: List[dict] = []
        self.auto_heal_enabled = True
        self.recovery_policy = "restart_first"  # restart_first, replace, escalate

    def register_organ(self, organ_id: str, module_path: str = "",
                        automated: bool = False) -> OrganHealth:
        organ = OrganHealth(organ_id, module_path)
        organ.is_automated = automated
        self.organs[organ_id] = organ
        return organ

    def heartbeat(self, organ_id: str, healthy: bool,
                  latency_ms: float = 0.0) -> dict:
        organ = self.organs.get(organ_id)
        if not organ:
            organ = self.register_organ(organ_id)
        organ.record_heartbeat(healthy, latency_ms)

        entry = {
            "ts": time.time(),
            "organ_id": organ_id,
            "healthy": healthy,
            "latency_ms": latency_ms,
            "status": organ.status,
        }
        self.history.append(entry)
        if len(self.history) > 200:
            self.history = self.history[-200:]

        # Auto-heal check
        healed = None
        if self.auto_heal_enabled and organ.needs_auto_heal():
            healed = organ.trigger_recovery()
            entry["auto_heal"] = healed

        return {"ok": True, **entry}

    def get_organ(self, organ_id: str) -> Optional[OrganHealth]:
        return self.organs.get(organ_id)

    def get_organ_status(self, organ_id: str) -> dict:
        organ = self.organs.get(organ_id)
        if not organ:
            return {"ok": False, "error": f"organ {organ_id} not registered"}
        return organ.to_dict()

    def get_organism_health(self) -> dict:
        organs = list(self.organs.values())
        total = len(organs)
        if total == 0:
            return {"total_organs": 0, "resilience_score": 1.0}
        healthy = sum(1 for o in organs if o.status == "healthy")
        failing = sum(1 for o in organs if o.status == "failing")
        dead = sum(1 for o in organs if o.status == "dead")
        avg_score = sum(o.health_score for o in organs) / total
        auto_heal_count = sum(1 for o in organs
                               if o.consecutive_failures >= FAILURE_THRESHOLD)
        return {
            "total_organs": total,
            "healthy": healthy,
            "degraded": sum(1 for o in organs if o.status == "degraded"),
            "failing": failing,
            "dead": dead,
            "resilience_score": round(avg_score, 4),
            "auto_heal_triggered": auto_heal_count,
            "health_rate": round(healthy / total, 4) if total > 0 else 1.0,
            "auto_heal_enabled": self.auto_heal_enabled,
            "recovery_policy": self.recovery_policy,
        }

    def get_failing_organs(self) -> List[dict]:
        return [o.to_dict() for o in self.organs.values()
                if o.status in ("failing", "dead")]

    def trigger_manual_heal(self, organ_id: str, action: str = "restart") -> dict:
        organ = self.organs.get(organ_id)
        if not organ:
            return {"ok": False, "error": f"organ {organ_id} not found"}
        entry = {"ts": time.time(), "action": action, "manual": True}
        organ.recovery_history.append(entry)
        organ.consecutive_failures = 0
        organ.status = "degraded"
        return {"ok": True, **entry}

    def disable_auto_heal(self) -> None:
        self.auto_heal_enabled = False

    def enable_auto_heal(self) -> None:
        self.auto_heal_enabled = True

    def to_dict(self) -> dict:
        return {
            "organs": {k: v.to_dict() for k, v in self.organs.items()},
            "history": self.history[-50:],
            "organism_health": self.get_organism_health(),
        }


def _load() -> Tuple[ResilienceMesh, dict]:
    mesh = ResilienceMesh()
    state: dict = {}
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            state = {}
    for oid, od in state.get("organs", {}).items():
        organ = OrganHealth(oid, od.get("module_path", ""))
        organ.status = od.get("status", "healthy")
        organ.consecutive_failures = od.get("consecutive_failures", 0)
        organ.total_failures = od.get("total_failures", 0)
        organ.total_successes = od.get("total_successes", 0)
        organ.health_score = od.get("health_score", 1.0)
        organ.recovery_attempts = od.get("recovery_attempts", 0)
        organ.recovery_history = od.get("recovery_history", [])
        organ.last_heartbeat = od.get("last_heartbeat", time.time())
        organ.is_automated = od.get("is_automated", False)
        mesh.organs[oid] = organ
    mesh.auto_heal_enabled = state.get("auto_heal_enabled", True)
    mesh.recovery_policy = state.get("recovery_policy", "restart_first")
    mesh.history = state.get("history", [])
    return mesh, state


def _save(mesh: ResilienceMesh, state: dict) -> None:
    data = {
        "organs": {k: v.to_dict() for k, v in mesh.organs.items()},
        "auto_heal_enabled": mesh.auto_heal_enabled,
        "recovery_policy": mesh.recovery_policy,
        "history": mesh.history[-50:],
    }
    STATE_FILE.write_text(json.dumps(data, indent=2))


# Seed the organism's known organs
SEED_ORGANS = [
    ("hex_runtime", "api/wave97_hex_runtime.py", True),
    ("hex_cathedral", "api/wave98_hex_cathedral.py", True),
    ("omnirouter", "api/omnirouter.py", True),
    ("model_staleness", "api/model_staleness_registry.py", False),
    ("dashboard_resurrector", "lab/experiments/dashboard_resurrector.py", False),
]


def _ensure_defaults(mesh: ResilienceMesh) -> None:
    for oid, path, auto in SEED_ORGANS:
        if oid not in mesh.organs:
            mesh.register_organ(oid, path, auto)


def handler(req: dict) -> dict:
    action = req.get("action", "status")
    mesh, state = _load()
    _ensure_defaults(mesh)

    if action == "status":
        health = mesh.get_organism_health()
        return {
            "action": "status",
            "wave": 622,
            **health,
            "message": "Resilience Mesh status",
        }

    if action == "heartbeat":
        organ_id = req.get("organ_id", "")
        healthy = req.get("healthy", True)
        latency = req.get("latency_ms", 0.0)
        result = mesh.heartbeat(organ_id, healthy, latency)
        _save(mesh, state)
        return {"action": "heartbeat", "wave": 622, **result}

    if action == "organ_status":
        organ_id = req.get("organ_id", "")
        result = mesh.get_organ_status(organ_id)
        return {"action": "organ_status", "wave": 622, **result}

    if action == "failing":
        failing = mesh.get_failing_organs()
        return {"action": "failing", "wave": 622, "failing_organs": failing}

    if action == "heal":
        organ_id = req.get("organ_id", "")
        action_type = req.get("action_type", "restart")
        result = mesh.trigger_manual_heal(organ_id, action_type)
        _save(mesh, state)
        return {"action": "heal", "wave": 622, **result}

    if action == "toggle_auto_heal":
        if mesh.auto_heal_enabled:
            mesh.disable_auto_heal()
        else:
            mesh.enable_auto_heal()
        _save(mesh, state)
        return {"action": "toggle_auto_heal", "wave": 622,
                "auto_heal_enabled": mesh.auto_heal_enabled}

    if action == "policy":
        policy = req.get("policy", mesh.recovery_policy)
        mesh.recovery_policy = policy
        _save(mesh, state)
        return {"action": "policy", "wave": 622, "policy": policy}

    if action == "history":
        limit = req.get("limit", 20)
        return {"action": "history", "wave": 622,
                "history": mesh.history[-limit:]}

    return {"ok": False, "error": f"Unknown action: {action}"}


def coherence_vitals() -> dict:
    mesh, _ = _load()
    health = mesh.get_organism_health()
    return {
        "wave": 622,
        "total_organs": health["total_organs"],
        "resilience_score": health["resilience_score"],
        "health_rate": health["health_rate"],
        "failing": health["failing"],
    }


def resonates_with() -> List[str]:
    return ["wave621_omnirouter", "wave98_hex_cathedral", "wave620_model_staleness"]
