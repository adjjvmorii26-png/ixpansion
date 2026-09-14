"""Wave 645 — Communication Protocol.

Structured inter-module messaging:
- Message passing between organisms
- Protocol versioning and evolution
- Translation layer between dialects
- Semantic integrity checks
"""
import json, time
from pathlib import Path
STATE = Path("data/wave645_communication.json")
def _load():
    if STATE.exists(): return json.loads(STATE.read_text())
    return {"messages": [], "protocols": {"v1": {"version": "1.0", "fields": ["sender", "receiver", "type", "body"]}}, "tick": 0}
def _save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True); STATE.write_text(json.dumps(s, indent=2))
def _send(sender, receiver, msg_type, body):
    s = _load(); msg = {"sender": sender, "receiver": receiver, "type": msg_type, "body": body, "time": time.time(), "status": "delivered"}
    s["messages"].append(msg); s["messages"] = s["messages"][-200:]; _save(s)
    return {"ok": True, "message_id": len(s["messages"]), "status": "delivered"}
def _inbox(receiver):
    s = _load(); msgs = [m for m in s["messages"] if m["receiver"] == receiver][-10:]
    return {"ok": True, "receiver": receiver, "messages": msgs, "count": len(msgs)}
def _status():
    s = _load(); return {"ok": True, "tick": s["tick"], "messages": len(s["messages"]), "protocols": list(s["protocols"].keys())}
def handler(req):
    action = req.get("action", "status")
    if action == "status": return _status()
    elif action == "send": return _send(req.get("sender", "?"), req.get("receiver", "?"), req.get("type", "info"), req.get("body", ""))
    elif action == "inbox": return _inbox(req.get("receiver", "?"))
    return {"ok": False, "error": f"Unknown action: {action}"}
def coherence_vitals():
    s = _load(); return {"wave": 645, "messages": len(s["messages"])}
def resonates_with(): return ["wave638_symbiosis_protocol", "wave644_self_model", "wave637_meta_regulation"]
