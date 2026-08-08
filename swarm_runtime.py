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
from typing import Dict

from fastapi import FastAPI, Header, HTTPException


app = FastAPI(title="IXPANSION Swarm", version="1.0.0")
nodes: Dict[str, dict] = {}


def _token_is_valid(token: str | None) -> bool:
    configured = os.getenv("SWARM_TOKEN", "")
    return not configured or token == configured


def _require_token(token: str | None) -> None:
    if not _token_is_valid(token):
        raise HTTPException(status_code=401, detail="invalid swarm token")


@app.get("/health")
def health() -> dict:
    return {"status": "healthy", "role": os.getenv("SWARM_ROLE", "unknown")}


@app.post("/register")
def register(node_id: str, token: str | None = Header(default=None, alias="X-Swarm-Token")) -> dict:
    _require_token(token)
    now = time.time()
    nodes[node_id] = {"node_id": node_id, "last_seen": now}
    return {"registered": True, "node_id": node_id, "last_seen": now}


@app.get("/status")
def status(token: str | None = Header(default=None, alias="X-Swarm-Token")) -> dict:
    _require_token(token)
    return {"role": os.getenv("SWARM_ROLE", "unknown"), "nodes": nodes}


def _register_with_hub() -> None:
    hub = os.getenv("SWARM_HUB", "http://hub:8765").rstrip("/")
    token = os.getenv("SWARM_TOKEN", "")
    node_id = os.getenv("SWARM_NODE_ID") or f"worker-{socket.gethostname()}-{uuid.uuid4().hex[:8]}"
    request = urllib.request.Request(
        f"{hub}/register?node_id={urllib.parse.quote(node_id)}",
        headers={"X-Swarm-Token": token},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        response.read()


def run_worker() -> None:
    while True:
        try:
            _register_with_hub()
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            print(json.dumps({"event": "worker_register_failed", "error": str(exc)}))
        time.sleep(10)


if __name__ == "__main__":
    if os.getenv("SWARM_ROLE", "worker") == "worker":
        run_worker()