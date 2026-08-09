"""Minimal role-based runtime for the local multi-container swarm demo."""

from __future__ import annotations

import json
import os
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from typing import Dict, Optional

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel


app = FastAPI(title="IXPANSION Swarm", version="1.0.0")
nodes: Dict[str, dict] = {}
tasks: Dict[str, dict] = {}
MAX_TASKS = 100
TASK_LEASE_SECONDS = 30.0
NODE_STALE_SECONDS = 30.0


def _token_is_valid(token: str | None) -> bool:
    configured = os.getenv("SWARM_TOKEN", "")
    return not configured or token == configured


def _require_token(token: str | None) -> None:
    if not _token_is_valid(token):
        raise HTTPException(status_code=401, detail="invalid swarm token")


class HeartbeatRequest(BaseModel):
    node_id: str
    load: float = 0.0
    capacity: float = 1.0
    health: float = 1.0


class TaskRequest(BaseModel):
    task: str
    task_id: Optional[str] = None


class TaskCompletionRequest(BaseModel):
    node_id: str
    result: str = "completed"


@app.get("/health")
def health() -> dict:
    return {"status": "healthy", "role": os.getenv("SWARM_ROLE", "unknown")}


@app.post("/register")
def register(node_id: str, token: str | None = Header(default=None, alias="X-Swarm-Token")) -> dict:
    _require_token(token)
    now = time.time()
    previous = nodes.get(node_id, {})
    nodes[node_id] = {
        "node_id": node_id,
        "last_seen": now,
        "load": previous.get("load", 0.0),
        "capacity": previous.get("capacity", 1.0),
        "health": previous.get("health", 1.0),
        "status": "ready",
    }
    return {"registered": True, "node_id": node_id, "last_seen": now}


@app.post("/heartbeat")
def heartbeat(
    request: HeartbeatRequest,
    token: str | None = Header(default=None, alias="X-Swarm-Token"),
) -> dict:
    _require_token(token)
    if request.node_id not in nodes:
        raise HTTPException(status_code=404, detail="node is not registered")
    if not 0 <= request.load <= 1 or not 0 <= request.capacity <= 1 or not 0 <= request.health <= 1:
        raise HTTPException(status_code=422, detail="load, capacity, and health must be between 0 and 1")
    nodes[request.node_id].update(
        last_seen=time.time(),
        load=request.load,
        capacity=request.capacity,
        health=request.health,
        status="ready" if request.health >= 0.5 and request.capacity > 0 else "degraded",
    )
    return {"node_id": request.node_id, "accepted": True, "state": nodes[request.node_id]}


@app.post("/tasks")
def enqueue_task(
    request: TaskRequest,
    token: str | None = Header(default=None, alias="X-Swarm-Token"),
) -> dict:
    _require_token(token)
    if not request.task.strip():
        raise HTTPException(status_code=422, detail="task is required")
    task_id = request.task_id or uuid.uuid4().hex
    if task_id in tasks:
        return {"task_id": task_id, "status": tasks[task_id]["status"], "replayed": True}
    queued = sum(item["status"] == "queued" for item in tasks.values())
    if queued >= MAX_TASKS:
        raise HTTPException(status_code=429, detail="swarm task queue is full")
    tasks[task_id] = {
        "task_id": task_id,
        "task": request.task.strip(),
        "status": "queued",
        "created_at": time.time(),
        "assigned_to": None,
        "lease_expires_at": None,
        "result": None,
    }
    return {"task_id": task_id, "status": "queued", "replayed": False}


@app.get("/tasks/claim")
def claim_task(
    node_id: str,
    token: str | None = Header(default=None, alias="X-Swarm-Token"),
) -> dict:
    _require_token(token)
    if node_id not in nodes:
        raise HTTPException(status_code=404, detail="node is not registered")
    node = nodes[node_id]
    if (
        node["status"] == "degraded"
        or node["health"] < 0.5
        or node["capacity"] <= 0
        or time.time() - node["last_seen"] > NODE_STALE_SECONDS
    ):
        raise HTTPException(status_code=409, detail="node is not eligible for work")
    now = time.time()
    for item in tasks.values():
        if item["status"] == "assigned" and item["lease_expires_at"] < now:
            item.update(status="queued", assigned_to=None, lease_expires_at=None)
    for item in tasks.values():
        if item["status"] == "queued":
            item.update(
                status="assigned",
                assigned_to=node_id,
                lease_expires_at=now + TASK_LEASE_SECONDS,
            )
            nodes[node_id]["status"] = "working"
            return {"task": item}
    return {"task": None}


@app.post("/tasks/{task_id}/complete")
def complete_task(
    task_id: str,
    request: TaskCompletionRequest,
    token: str | None = Header(default=None, alias="X-Swarm-Token"),
) -> dict:
    _require_token(token)
    item = tasks.get(task_id)
    if item is None:
        raise HTTPException(status_code=404, detail="task not found")
    if item["status"] == "completed":
        return {"task": item, "replayed": True}
    if item["assigned_to"] != request.node_id:
        raise HTTPException(status_code=409, detail="task is assigned to another node")
    if item["lease_expires_at"] < time.time():
        item.update(status="queued", assigned_to=None, lease_expires_at=None)
        raise HTTPException(status_code=409, detail="task lease expired")
    item.update(status="completed", result=request.result, completed_at=time.time())
    nodes[request.node_id]["status"] = "ready"
    return {"task": item, "replayed": False}


@app.get("/status")
def status(token: str | None = Header(default=None, alias="X-Swarm-Token")) -> dict:
    _require_token(token)
    return {"role": os.getenv("SWARM_ROLE", "unknown"), "nodes": nodes, "tasks": tasks}


def _register_with_hub(node_id: Optional[str] = None) -> None:
    hub = os.getenv("SWARM_HUB", "http://hub:8765").rstrip("/")
    token = os.getenv("SWARM_TOKEN", "")
    node_id = node_id or os.getenv("SWARM_NODE_ID") or f"worker-{socket.gethostname()}-{uuid.uuid4().hex[:8]}"
    request = urllib.request.Request(
        f"{hub}/register?node_id={urllib.parse.quote(node_id)}",
        headers={"X-Swarm-Token": token},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        response.read()


def _heartbeat_with_hub(node_id: str) -> None:
    hub = os.getenv("SWARM_HUB", "http://hub:8765").rstrip("/")
    token = os.getenv("SWARM_TOKEN", "")
    payload = json.dumps({"node_id": node_id, "load": 0.1, "capacity": 0.9, "health": 1.0}).encode()
    request = urllib.request.Request(
        f"{hub}/heartbeat",
        data=payload,
        headers={"X-Swarm-Token": token, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        response.read()


def _claim_from_hub(node_id: str) -> Optional[dict]:
    hub = os.getenv("SWARM_HUB", "http://hub:8765").rstrip("/")
    token = os.getenv("SWARM_TOKEN", "")
    request = urllib.request.Request(
        f"{hub}/tasks/claim?node_id={urllib.parse.quote(node_id)}",
        headers={"X-Swarm-Token": token},
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        return json.loads(response.read().decode()).get("task")


def _complete_at_hub(node_id: str, task_id: str, result: str) -> None:
    hub = os.getenv("SWARM_HUB", "http://hub:8765").rstrip("/")
    token = os.getenv("SWARM_TOKEN", "")
    payload = json.dumps({"node_id": node_id, "result": result}).encode()
    request = urllib.request.Request(
        f"{hub}/tasks/{urllib.parse.quote(task_id)}/complete",
        data=payload,
        headers={"X-Swarm-Token": token, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        response.read()


def run_worker() -> None:
    node_id = os.getenv("SWARM_NODE_ID") or f"worker-{socket.gethostname()}-{uuid.uuid4().hex[:8]}"
    while True:
        try:
            _register_with_hub(node_id)
            _heartbeat_with_hub(node_id)
            task = _claim_from_hub(node_id)
            if task:
                _complete_at_hub(node_id, task["task_id"], f"completed by {node_id}")
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            print(json.dumps({"event": "worker_cycle_failed", "error": str(exc)}))
        time.sleep(10)


if __name__ == "__main__":
    if os.getenv("SWARM_ROLE", "worker") == "worker":
        run_worker()