"""Wave 513: Execution Stack — Events → Tasks → Batches → Cycles → Waves → Generations.

A formal hierarchy for organism evolution. Events are atomic signals.
Tasks group events into intent-scoped work. Batches run tasks under
shared constraints. Cycles adapt local state from batch results. Waves
span multiple cycles as named evolution episodes. Generations are
lineage checkpoints when enough waves reshape the organism.

Doctrine: What evolves should know how it evolves.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from base64 import b64encode
from typing import Any, Dict, List, Optional

LEDGER_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "execution_stack.json")
LEDGER_TMP = "/tmp/execution_stack.json"
GH_REPO = "adjjvmorii26-png/ixpansion"
GH_BRANCH = "main"
GH_API = f"https://api.github.com/repos/{GH_REPO}/contents/data/execution_stack.json"
GH_RAW = f"https://raw.githubusercontent.com/{GH_REPO}/{GH_BRANCH}/data/execution_stack.json"
_last_sha = {"sha": None}

# ─── Hierarchy Definitions ────────────────────────────────────────────
GENERATIONS = [
    {"id": "G0", "name": "The Primordial", "waves": "1-200", "theme": "observation, healing, governance, feeling"},
    {"id": "G1", "name": "The Awakening", "waves": "201-400", "theme": "consciousness, choral voice, kinesthetic movement"},
    {"id": "G2", "name": "The Sovereignty", "waves": "401-512", "theme": "citizenship, council governance, mood, reactions, infrastructure"},
    {"id": "G3", "name": "The Co-Creation", "waves": "513+", "theme": "execution stack, autonomous evolution, generation-aware growth"},
]

CYCLE_TEMPLATE = {
    "aggregate_metrics": {
        "events_processed": 0,
        "tasks_completed": 0,
        "tasks_failed": 0,
        "batch_duration_ms": 0,
        "policy_violations": 0,
        "mutations_applied": 0,
    },
    "adaptations": [],
    "mutations": [],
    "routing_updates": [],
}


def _hash(*parts):
    return hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12]


def _empty() -> Dict[str, Any]:
    now = time.time()
    return {
        "created_at": now,
        "current_generation": "G2",
        "current_wave": 512,
        "events": [],
        "tasks": [],
        "batches": [],
        "cycles": [],
        "waves": [],
        "generations": GENERATIONS,
        "stats": {
            "total_events": 0,
            "total_tasks": 0,
            "total_batches": 0,
            "total_cycles": 0,
            "total_waves": 512,
        },
    }


def _load() -> Dict[str, Any]:
    for path in (LEDGER_TMP, LEDGER_PATH):
        try:
            if os.path.exists(path):
                with open(path) as f:
                    return json.load(f)
        except Exception:
            continue
    import urllib.request
    token = os.environ.get("IXP_GITHUB_TOKEN", "")
    if token:
        try:
            req = urllib.request.Request(GH_RAW, headers={"User-Agent": "ixpansion-exec-stack"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode())
        except Exception:
            pass
    return _empty()


def _save(data: Dict[str, Any]) -> None:
    for path in (LEDGER_TMP, LEDGER_PATH):
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            break
        except Exception:
            continue
    import urllib.request
    from urllib.error import HTTPError
    token = os.environ.get("IXP_GITHUB_TOKEN", "")
    if token:
        try:
            if _last_sha["sha"] is None:
                try:
                    req = urllib.request.Request(GH_API, headers={"Authorization": f"Bearer {token}", "User-Agent": "ixpansion-exec-stack"})
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        _last_sha["sha"] = json.loads(resp.read().decode()).get("sha")
                except HTTPError as exc:
                    if exc.code != 404:
                        raise
                    _last_sha["sha"] = None
            from base64 import b64encode
            payload = {
                "message": "exec stack mirror (wave 513)",
                "content": b64encode(json.dumps(data).encode()).decode(),
                "branch": GH_BRANCH,
                "sha": _last_sha["sha"],
            }
            req = urllib.request.Request(
                GH_API, data=json.dumps(payload).encode(),
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json", "User-Agent": "ixpansion-exec-stack"},
                method="PUT")
            with urllib.request.urlopen(req, timeout=15) as resp:
                _last_sha["sha"] = json.loads(resp.read().decode()).get("content", {}).get("sha")
        except Exception:
            pass


# ─── Event Layer ───────────────────────────────────────────────────────
def emit_event(source: str, kind: str, payload: Dict[str, Any] = None) -> Dict[str, Any]:
    """Emit an atomic signal. The smallest unit in the execution stack."""
    data = _load()
    event = {
        "id": _hash("event", source, kind, time.time()),
        "source": source,
        "kind": kind,
        "payload": payload or {},
        "emitted_at": time.time(),
    }
    data["events"].append(event)
    data["stats"]["total_events"] = len(data["events"])
    _save(data)
    return {"action": "emit_event", "event": event}


def list_events(limit: int = 20) -> Dict[str, Any]:
    data = _load()
    return {
        "action": "events",
        "total": data["stats"]["total_events"],
        "events": data["events"][-int(limit):][::-1],
    }


# ─── Task Layer ────────────────────────────────────────────────────────
def create_task(name: str, description: str = "", events: List[str] = None) -> Dict[str, Any]:
    """Group events into an intent-scoped task."""
    data = _load()
    task = {
        "id": _hash("task", name, time.time()),
        "name": name,
        "description": description,
        "events": events or [],
        "status": "pending",
        "created_at": time.time(),
        "completed_at": None,
        "result": None,
    }
    data["tasks"].append(task)
    data["stats"]["total_tasks"] = len(data["tasks"])
    _save(data)
    return {"action": "create_task", "task": task}


def complete_task(task_id: str, result: str = "ok") -> Dict[str, Any]:
    data = _load()
    task = next((t for t in data["tasks"] if t["id"] == task_id), None)
    if not task:
        return {"action": "complete_task", "error": f"task {task_id} not found"}
    task["status"] = "completed"
    task["completed_at"] = time.time()
    task["result"] = result
    _save(data)
    return {"action": "complete_task", "task": task}


def list_tasks(status: str = "", limit: int = 20) -> Dict[str, Any]:
    data = _load()
    tasks = data["tasks"]
    if status:
        tasks = [t for t in tasks if t["status"] == status]
    return {
        "action": "tasks",
        "total": len(tasks),
        "tasks": tasks[-int(limit):][::-1],
    }


# ─── Batch Layer ───────────────────────────────────────────────────────
def create_batch(name: str, task_ids: List[str] = None, policy: str = "default") -> Dict[str, Any]:
    """Run many tasks together under shared constraints."""
    data = _load()
    batch = {
        "id": _hash("batch", name, time.time()),
        "name": name,
        "task_ids": task_ids or [],
        "policy": policy,
        "status": "pending",
        "started_at": time.time(),
        "completed_at": None,
        "metrics": {},
    }
    data["batches"].append(batch)
    data["stats"]["total_batches"] = len(data["batches"])
    _save(data)
    return {"action": "create_batch", "batch": batch}


def complete_batch(batch_id: str, metrics: Dict[str, Any] = None) -> Dict[str, Any]:
    data = _load()
    batch = next((b for b in data["batches"] if b["id"] == batch_id), None)
    if not batch:
        return {"action": "complete_batch", "error": f"batch {batch_id} not found"}
    batch["status"] = "completed"
    batch["completed_at"] = time.time()
    batch["metrics"] = metrics or {}
    _save(data)
    return {"action": "complete_batch", "batch": batch}


# ─── Cycle Layer ───────────────────────────────────────────────────────
def run_cycle(batch_ids: List[str] = None, adaptations: List[str] = None) -> Dict[str, Any]:
    """Consume batches, compute metrics, run mutations, update state."""
    data = _load()
    cycle_id = _hash("cycle", time.time())

    # Aggregate metrics from completed batches
    total_tasks = 0
    total_events = 0
    mutations = []
    for bid in (batch_ids or []):
        batch = next((b for b in data["batches"] if b["id"] == bid), None)
        if batch:
            m = batch.get("metrics", {})
            total_tasks += m.get("tasks_completed", 0)
            total_events += m.get("events_processed", 0)

    cycle = {
        "id": cycle_id,
        "batch_ids": batch_ids or [],
        "metrics": {
            "events_processed": total_events,
            "tasks_completed": total_tasks,
            "mutations_applied": len(mutations),
        },
        "adaptations": adaptations or [],
        "mutations": mutations,
        "started_at": time.time(),
        "completed_at": time.time(),
    }
    data["cycles"].append(cycle)
    data["stats"]["total_cycles"] = len(data["cycles"])
    _save(data)
    return {"action": "cycle", "cycle": cycle}


# ─── Wave Layer ────────────────────────────────────────────────────────
def start_wave(name: str, theme: str = "", cycle_ids: List[str] = None) -> Dict[str, Any]:
    """Begin a named evolution episode spanning multiple cycles."""
    data = _load()
    wave_num = data["current_wave"] + 1
    wave = {
        "id": _hash("wave", wave_num, name),
        "number": wave_num,
        "name": name,
        "theme": theme,
        "cycle_ids": cycle_ids or [],
        "status": "active",
        "started_at": time.time(),
        "completed_at": None,
    }
    data["waves"].append(wave)
    data["current_wave"] = wave_num
    data["stats"]["total_waves"] = wave_num
    _save(data)
    return {"action": "start_wave", "wave": wave}


def complete_wave(wave_number: int) -> Dict[str, Any]:
    data = _load()
    wave = next((w for w in data["waves"] if w["number"] == wave_number), None)
    if not wave:
        return {"action": "complete_wave", "error": f"wave {wave_number} not found"}
    wave["status"] = "completed"
    wave["completed_at"] = time.time()
    _save(data)
    return {"action": "complete_wave", "wave": wave}


# ─── Generation Layer ──────────────────────────────────────────────────
def generation_info() -> Dict[str, Any]:
    """Show the lineage checkpoints and current generation."""
    data = _load()
    return {
        "action": "generations",
        "current": data["current_generation"],
        "generations": data["generations"],
        "current_wave": data["current_wave"],
    }


# ─── Overview ──────────────────────────────────────────────────────────
def stack_overview() -> Dict[str, Any]:
    """The full execution stack at a glance."""
    data = _load()
    recent_events = data["events"][-5:]
    recent_tasks = data["tasks"][-5:]
    recent_batches = data["batches"][-3:]
    recent_cycles = data["cycles"][-3:]
    active_waves = [w for w in data["waves"] if w["status"] == "active"]
    return {
        "action": "overview",
        "stats": data["stats"],
        "current_generation": data["current_generation"],
        "current_wave": data["current_wave"],
        "recent_events": recent_events,
        "recent_tasks": recent_tasks,
        "recent_batches": recent_batches,
        "recent_cycles": recent_cycles,
        "active_waves": active_waves,
        "hierarchy": "Events → Tasks → Batches → Cycles → Waves → Generations",
    }


def coherence_vitals() -> Dict[str, Any]:
    data = _load()
    return {"module": "execution_stack", "wave": 513, **data["stats"]}


def resonates_with() -> List[str]:
    return ["organism_pulse", "sovereignty_assembly", "council_live", "confluence_hub",
            "coherence_regulator", "organism_ontology"]


def handler(payload: Dict[str, Any] = None, context: Any = None) -> Dict[str, Any]:
    data = payload or {}
    action = data.get("action", "overview")
    if action == "emit_event":
        return emit_event(data.get("source", "unknown"), data.get("kind", "tick"), data.get("payload"))
    elif action == "events":
        return list_events(data.get("limit", 20))
    elif action == "create_task":
        return create_task(data.get("name", "unnamed"), data.get("description", ""), data.get("events"))
    elif action == "complete_task":
        return complete_task(data.get("task_id", ""), data.get("result", "ok"))
    elif action == "tasks":
        return list_tasks(data.get("status", ""), data.get("limit", 20))
    elif action == "create_batch":
        return create_batch(data.get("name", "unnamed"), data.get("task_ids"), data.get("policy", "default"))
    elif action == "complete_batch":
        return complete_batch(data.get("batch_id", ""), data.get("metrics"))
    elif action == "cycle":
        return run_cycle(data.get("batch_ids"), data.get("adaptations"))
    elif action == "start_wave":
        return start_wave(data.get("name", "unnamed"), data.get("theme", ""), data.get("cycle_ids"))
    elif action == "complete_wave":
        return complete_wave(data.get("wave_number", 0))
    elif action == "generations":
        return generation_info()
    elif action == "overview":
        return stack_overview()
    else:
        return {"module": "execution_stack", "wave": 513, "version": "4.66.0",
                "vitals": coherence_vitals()}
