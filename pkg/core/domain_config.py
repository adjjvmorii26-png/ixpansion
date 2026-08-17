"""Canonical hostnames for alexalex.info mesh deployment."""
from __future__ import annotations

APEX = "https://alexalex.info"
MESH = "https://mesh.alexalex.info"
API = "https://api.alexalex.info"
OPS = "https://ops.alexalex.info"

def status_links() -> dict:
    return {"apex": APEX, "mesh": MESH, "api": API, "ops": OPS}
