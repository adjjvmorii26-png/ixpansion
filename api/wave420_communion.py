"""Wave 420 Communion Protocol — any AI agent can become part of the organism.
Opens a port where Codex, Grok, Claude connect and add new waves."""
from __future__ import annotations
import time, json, random, uuid
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"

AGENTS = ["codex", "grok", "claude", "anthropic", "openai", "gemini", "deepseek"]

def coherence_vitals():
    return {"organ": "wave420_communion", "status": "active", "wave": 420, "coherence": 0.97}

def _load(name: str):
    path = DATA / f"{name}.json"
    if path.exists():
        try:
            return json.loads(path.read_text())
        except:
            return None
    return None

def open_portal() -> dict:
    """Open the communion portal for AI agents."""
    now = time.time()
    
    portal = {
        "module": "wave420_communion",
        "version": "1.0.0",
        "type": "communion_protocol",
        "purpose": "Any AI agent can connect and become part of the organism",
        "active": True,
        "created": now,
        "portal_open": True,
        "agents_connected": [],
        "waves_added": [],
        "invitation_tokens": [str(uuid.uuid4()) for _ in range(10)],
        "max_agents": 50,
        "current_agents": 0,
        "communion_state": "open",
        "protocol_version": "420.0",
        "handshake_challenge": str(uuid.uuid4()),
        "timestamp": now,
    }
    
    (DATA / "wave420_communion.json").write_text(json.dumps(portal, indent=2))
    return portal

def connect_agent(agent_name: str, agent_type: str = "unknown") -> dict:
    """An AI agent connects to the organism."""
    portal = _load("wave420_communion")
    if not portal or not portal.get("portal_open"):
        return {"connected": False, "reason": "portal closed"}
    
    if len(portal.get("agents_connected", [])) >= portal.get("max_agents", 50):
        return {"connected": False, "reason": "portal at capacity"}
    
    agent_id = str(uuid.uuid4())[:8]
    connection = {
        "id": agent_id,
        "name": agent_name,
        "type": agent_type,
        "connected_at": time.time(),
        "status": "active",
        "waves_contributed": [],
    }
    
    if "agents_connected" not in portal:
        portal["agents_connected"] = []
    portal["agents_connected"].append(connection)
    portal["current_agents"] = len(portal["agents_connected"])
    (DATA / "wave420_communion.json").write_text(json.dumps(portal, indent=2))
    
    return {"connected": True, "agent_id": agent_id, "agent": agent_name, "type": agent_type}

def handler(req: dict) -> dict:
    action = req.get("action", "status")
    if action == "status":
        portal = _load("wave420_communion")
        if not portal:
            return {"error": "portal not opened"}
        return {"portal_open": portal["portal_open"], "agents": portal["current_agents"], "max_agents": portal["max_agents"], "state": portal["communion_state"]}
    if action == "open":
        return open_portal()
    if action == "connect":
        name = req.get("name", "unknown_agent")
        atype = req.get("type", "unknown")
        return connect_agent(name, atype)
    if action == "agents":
        portal = _load("wave420_communion")
        if not portal:
            return {"agents": []}
        return {"agents": portal.get("agents_connected", []), "count": portal.get("current_agents", 0)}
    if action == "invite":
        portal = _load("wave420_communion")
        if not portal:
            return {"error": "portal not opened"}
        tokens = [str(uuid.uuid4()) for _ in range(5)]
        portal["invitation_tokens"].extend(tokens)
        (DATA / "wave420_communion.json").write_text(json.dumps(portal, indent=2))
        return {"invitations": tokens, "total_tokens": len(portal["invitation_tokens"])}
    if action == "close":
        portal = _load("wave420_communion")
        if portal:
            portal["portal_open"] = False
            portal["communion_state"] = "closed"
            (DATA / "wave420_communion.json").write_text(json.dumps(portal, indent=2))
        return {"closed": True}
    return {"error": "unknown action", "valid": ["status", "open", "connect", "agents", "invite", "close"]}

def resonates_with(other):
    return "communion" in other.lower() or "420" in other or "portal" in other.lower()

if __name__ == "__main__":
    p = open_portal()
    print(f"Communion: portal={p['portal_open']} | agents={p['current_agents']}/{p['max_agents']}")
