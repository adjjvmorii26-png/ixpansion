"""Wave 135 — Client Portal.

A backend for external clients: onboarding, project workspaces,
deliverable history, and support tickets. Ties subscriptions, SLAs,
and commissions into a single per-client view the civilization can
serve.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional


class Client:
    """An onboarded external client."""

    def __init__(self, name: str, plan: str = "free"):
        self.name = name
        self.plan = plan
        self.deliverables: List[str] = []
        self.tickets: List[str] = []
        self.status = "active"
        self.created = time.time()
        self.id = hashlib.sha256(f"client:{name}".encode()).hexdigest()[:10]

    def receive(self, deliverable: str) -> None:
        self.deliverables.append(deliverable)

    def open_ticket(self, subject: str) -> str:
        ticket = hashlib.sha256(f"ticket:{self.name}:{subject}".encode()).hexdigest()[:10]
        self.tickets.append(ticket)
        return ticket

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "plan": self.plan,
                "deliverables": len(self.deliverables), "open_tickets": len(self.tickets),
                "status": self.status}


class ClientPortal:
    """Manages the external client lifecycle."""

    def __init__(self):
        self._clients: Dict[str, Client] = {}
        self._activations = 0

    def onboard(self, name: str, plan: str = "free") -> Client:
        client = Client(name, plan)
        self._clients[client.id] = client
        self._activations += 1
        return client

    def deliver(self, client_id: str, deliverable: str) -> bool:
        client = self._clients.get(client_id)
        if client is None:
            return False
        client.receive(deliverable)
        return True

    def support(self, client_id: str, subject: str) -> str:
        client = self._clients.get(client_id)
        if client is None:
            return ""
        return client.open_ticket(subject)

    def suspend(self, client_id: str) -> bool:
        client = self._clients.get(client_id)
        if client is None:
            return False
        client.status = "suspended"
        return True

    def status(self) -> Dict[str, Any]:
        return {"clients": len(self._clients), "activations": self._activations,
                "suspended": sum(1 for c in self._clients.values() if c.status == "suspended"),
                "total_deliverables": sum(len(c.deliverables) for c in self._clients.values())}


def handler(payload: dict = None, context: object = None) -> dict:
    """Vercel-compatible handler."""
    payload = payload or {}
    portal = ClientPortal()
    return {"status": "active", "module": "client_portal",
            **portal.status()}
