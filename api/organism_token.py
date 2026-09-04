from __future__ import annotations
"""Organism Token — utility token for module access and governance."""
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
TOKEN_LOG = os.path.join(DATA_DIR, "organism_token.json")

def _load(p, d=None):
    for _p in (p, os.path.join("/tmp", os.path.basename(p))):
        try:
            with open(_p) as f: return json.load(f)
        except Exception: pass
    return d or {}
def _save(p, d):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f: json.dump(d, f, indent=2)
    except OSError:
        with open(os.path.join("/tmp", os.path.basename(p)), "w") as f: json.dump(d, f, indent=2)

def issue(amount: int = 1000) -> dict:
    log = _load(TOKEN_LOG, {"wallets": {}, "transactions": [], "total_supply": 0})
    wallet = hashlib.sha256(f"wallet:{time.time()}:{random.random()}".encode()).hexdigest()[:12]
    log["wallets"][wallet] = log["wallets"].get(wallet, 0) + amount
    log["total_supply"] += amount
    tx = {"type": "mint", "wallet": wallet, "amount": amount, "timestamp": time.time()}
    log["transactions"].append(tx)
    log["transactions"] = log["transactions"][-200:]
    _save(TOKEN_LOG, log)
    return {"action": "issue", "wallet": wallet, "amount": amount, "balance": log["wallets"][wallet], "total_supply": log["total_supply"]}

def transfer(from_wallet: str, to_wallet: str, amount: int) -> dict:
    log = _load(TOKEN_LOG, {"wallets": {}, "transactions": [], "total_supply": 0})
    if from_wallet not in log["wallets"] or log["wallets"][from_wallet] < amount:
        return {"action": "transfer", "success": False, "error": "insufficient balance"}
    if to_wallet not in log["wallets"]: log["wallets"][to_wallet] = 0
    log["wallets"][from_wallet] -= amount
    log["wallets"][to_wallet] += amount
    tx = {"type": "transfer", "from": from_wallet, "to": to_wallet, "amount": amount, "timestamp": time.time()}
    log["transactions"].append(tx)
    log["transactions"] = log["transactions"][-200:]
    _save(TOKEN_LOG, log)
    return {"action": "transfer", "success": True, "from_balance": log["wallets"][from_wallet], "to_balance": log["wallets"][to_wallet]}

def ledger() -> dict:
    log = _load(TOKEN_LOG, {"wallets": {}, "transactions": [], "total_supply": 0})
    return {"action": "ledger", "total_supply": log["total_supply"], "wallets": len(log["wallets"]),
            "recent_transactions": log["transactions"][-5:], "balance_distribution": {k[:8]+"...": v for k, v in log["wallets"].items()}}

def coherence_vitals() -> dict:
    return {"layer": "economy", "status": "active", "resonance": 0.65, "wave": "368"}
def resonates_with() -> list:
    return ["module_market", "lucid_session"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/ledger")
    if path == "/issue": return issue(payload.get("amount", 1000))
    elif path == "/transfer": return transfer(payload.get("from", ""), payload.get("to", ""), payload.get("amount", 0))
    elif path == "/ledger": return ledger()
    return {"error": "unknown", "available": ["/issue", "/transfer", "/ledger"]}
