"""Wave 638 — Symbiosis Protocol.

Contracts for external agents, codebases, and organisms to join the
IXPANSION organism. Handles:
- Partnership handshakes (join / leave / renew)
- Trust negotiation & resource sharing
- Mutual resonance scoring between organisms
- Symbiosis lifecycle (courting → joint → diverging → separated)
"""
import json, time, hashlib
from pathlib import Path

STATE = Path("data/wave638_symbiosis_protocol.json")

def _load():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {
        "partners": {},
        "handshakes": [],
        "resonance_scores": {},
        "resource_ledger": {},
        "protocol_version": "1.0.0",
    }

def _save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s, indent=2))

def _now():
    return time.time()

def _fingerprint(partner_id):
    """Create a stable identity fingerprint for a partner."""
    return hashlib.sha256(partner_id.encode()).hexdigest()[:16]

def _handshake(partner_id, platform="github", capabilities=None):
    """Initiate a partnership handshake."""
    s = _load()
    s["handshakes"].append({
        "partner": partner_id,
        "platform": platform,
        "capabilities": capabilities or [],
        "time": _now(),
        "state": "received",
    })
    s["handshakes"] = s["handshakes"][-100:]
    _save(s)
    return {"ok": True, "handshake_id": f"HS_{_fingerprint(partner_id)}", "state": "received"}

def _engage(partner_id, platform="github", capabilities=None, trust_threshold=0.5):
    """Accept a partner into the organism (or renew an existing bond)."""
    s = _load()
    now = _now()
    fp = _fingerprint(partner_id)

    if fp not in s["partners"]:
        s["partners"][fp] = {
            "partner_id": partner_id,
            "platform": platform,
            "capabilities": capabilities or [],
            "joined_at": now,
            "last_contact": now,
            "trust": 0.6,
            "status": "courting",
            "handshake_id": f"HS_{fp}",
        }

    p = s["partners"][fp]
    p["status"] = "joint"
    p["last_contact"] = now
    s["partners"][fp] = p
    _save(s)
    return {"ok": True, "partner": partner_id, "status": "joint", "trust": p["trust"]}

def _resonate(a_name, b_name, signal_strength=0.5):
    """Score mutual resonance between this organism and a partner."""
    s = _load()
    fp = _fingerprint(b_name)
    key = f"{a_name}↔{b_name}"
    s["resonance_scores"][key] = {
        "partner": b_name,
        "signal_strength": signal_strength,
        "last_measured": _now(),
        "score": round(min(1.0, signal_strength * (0.4 + 0.6 * (len(s["partners"]) > 0))), 3),
    }
    _save(s)
    return {"ok": True, "resonance": s["resonance_scores"][key]}

def _share_resource(partner_id, resource, amount=1.0):
    """Record resource sharing with a partner."""
    s = _load()
    fp = _fingerprint(partner_id)
    ledger = s["resource_ledger"].setdefault(fp, {})
    ledger[resource] = ledger.get(resource, 0) + amount
    s["resource_ledger"][fp] = ledger
    _save(s)
    return {"ok": True, "partner": partner_id, "resource": resource, "total": ledger[resource]}

def _status():
    s = _load()
    partners = []
    for fp, p in s["partners"].items():
        partners.append({
            "partner": p["partner_id"],
            "platform": p.get("platform", "github"),
            "status": p["status"],
            "trust": round(p["trust"], 3),
            "joined_at": p["joined_at"],
            "capabilities": p.get("capabilities", [])[:5],
        })
    return {
        "protocol_version": s["protocol_version"],
        "total_partners": len(partners),
        "joint_partners": len([p for p in partners if p["status"] == "joint"]),
        "partner_list": partners[:20],
        "recent_handshakes": s["handshakes"][-5:],
    }

def _relations_map():
    """Return the symbiosis map — every partner relationship."""
    s = _load()
    return {
        "resonance_scores": s["resonance_scores"],
        "resource_ledger": s["resource_ledger"],
    }

def handler(req):
    action = req.get("action", "status")
    if action == "status":
        return {"ok": True, **_status()}
    elif action == "handshake":
        return {"ok": True, **_handshake(
            req.get("partner_id", "unknown"),
            req.get("platform", "github"),
            req.get("capabilities", []),
        )}
    elif action == "engage":
        return {"ok": True, **_engage(
            req.get("partner_id", "unknown"),
            req.get("platform", "github"),
            req.get("capabilities", []),
            req.get("trust_threshold", 0.5),
        )}
    elif action == "resonate":
        return {"ok": True, **_resonate(
            req.get("a", "ixpansion"),
            req.get("b", "unknown"),
            req.get("signal_strength", 0.5),
        )}
    elif action == "share":
        return {"ok": True, **_share_resource(
            req.get("partner_id", "unknown"),
            req.get("resource", "data"),
            req.get("amount", 1.0),
        )}
    elif action == "relations":
        return {"ok": True, **_relations_map()}
    return {"ok": False, "error": f"Unknown action: {action}"}

def coherence_vitals():
    s = _load()
    return {"wave": 638, "partners": len(s["partners"]), "protocol": s["protocol_version"]}

def resonates_with():
    return ["wave637_meta_regulation", "omnirouter", "wave622_resilience_mesh", "wave420_communion_protocol"]
