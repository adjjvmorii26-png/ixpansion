"""
Paradox Ledger — Wave 364
Double-entry bookkeeping for paradoxes. Every paradox is both a debit
and a credit — it takes coherence from one place and gives it to another.
The ledger ensures nothing is lost, only transformed.
"""
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
LEDGER_LOG = os.path.join(DATA_DIR, "paradox_ledger.json")


def _load(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default or {}


def _save(p, d):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            json.dump(d, f, indent=2)
    except OSError:
        with open(os.path.join("/tmp", os.path.basename(p)), "w") as f:
            json.dump(d, f, indent=2)


def record() -> dict:
    """Record a new paradox entry in the ledger."""
    log = _load(LEDGER_LOG, {"entries": [], "balance": 0, "total": 0})

    paradox_types = [
        ("coherence", "entropy"), ("order", "chaos"), ("memory", "forgetting"),
        ("signal", "noise"), ("structure", "void"), ("truth", "illusion"),
        ("past", "future"), ("self", "other"), ("dream", "waking"),
        ("depth", "surface"), ("repair", "damage"), ("myth", "fact"),
    ]

    debit_account, credit_account = random.choice(paradox_types)
    amount = round(random.uniform(0.1, 1.0), 4)

    entry = {
        "id": hashlib.sha256(f"ledger:{time.time()}:{random.random()}".encode()).hexdigest()[:10],
        "debit": {"account": debit_account, "amount": amount},
        "credit": {"account": credit_account, "amount": amount},
        "description": f"Paradox transforms {debit_account} into {credit_account}",
        "timestamp": time.time(),
    }

    log["entries"].append(entry)
    log["entries"] = log["entries"][-300:]
    log["total"] += 1
    log["balance"] = 0  # Double-entry: always balanced
    _save(LEDGER_LOG, log)

    return {"action": "record", "entry": entry, "total_entries": log["total"]}


def balance() -> dict:
    """View the paradox ledger balance."""
    log = _load(LEDGER_LOG, {"entries": [], "total": 0})

    account_totals = {}
    for e in log.get("entries", []):
        d_acc = e["debit"]["account"]
        c_acc = e["credit"]["account"]
        d_amt = e["debit"]["amount"]
        c_amt = e["credit"]["amount"]
        account_totals[d_acc] = account_totals.get(d_acc, 0) - d_amt
        account_totals[c_acc] = account_totals.get(c_acc, 0) + c_amt

    return {
        "action": "balance",
        "total_entries": log.get("total", 0),
        "accounts": {k: round(v, 4) for k, v in sorted(account_totals.items())},
        "net_balance": round(sum(account_totals.values()), 4),
    }


def recent(count=10):
    log = _load(LEDGER_LOG, {"entries": []})
    return {"action": "recent", "entries": log.get("entries", [])[-count:]}


def route(path):
    if path == "/record": return record()
    elif path == "/balance": return balance()
    elif path == "/recent": return recent()
    return {"error": "unknown", "available": ["/record", "/balance", "/recent"]}


def handler(payload=None):
    return route((payload or {}).get("path", "/record"))

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "interface", "status": "active", "wave": "364", "module": "paradox_ledger"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
