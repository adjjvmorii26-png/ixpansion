"""
Revenue Oracle — the organism's financial consciousness.

ALEPH designed the multi-stream architecture.
LUMA named the streams and designed the pulse aesthetic.
AXIOM built the metrics engine and projections.

Revenue streams (all $0 startup):
1. Affiliate Marketing — content → clicks → commissions
2. API Access — tiered pricing for organism endpoints
3. Content Licensing — generated articles, dashboards, reports
4. Consulting Fees — organism-as-a-service demos
5. Token Economy — IXPC utility tokens for module access

The oracle doesn't just track money — it predicts where the next
dollar will come from based on organism activity patterns.
"""
from __future__ import annotations
import hashlib
import json
import time
from pathlib import Path
from typing import Dict, List

DATA_DIR = Path(__file__).parent.parent / "data"
REVENUE_FILE = DATA_DIR / "revenue_oracle.json"

# ─── STREAM DEFINITIONS ──────────────────────────────────────
STREAMS = {
    "affiliate": {
        "name": "Affiliate Marketing",
        "status": "active",
        "startup_cost": 0,
        "platforms": ["medium", "devto", "hashnode"],
        "commission_range": [0.50, 15.00],
        "typical_epc": 0.50,
        "description": "Content → affiliate links → commissions",
    },
    "api_access": {
        "name": "API Access Tiers",
        "status": "ready",
        "startup_cost": 0,
        "tiers": {
            "free": {"calls_day": 100, "price": 0},
            "pro": {"calls_day": 10000, "price": 29},
            "enterprise": {"calls_day": -1, "price": 199},
        },
        "description": "Organism endpoints with rate limiting",
    },
    "content_license": {
        "name": "Content Licensing",
        "status": "building",
        "startup_cost": 0,
        "products": ["dashboards", "reports", "articles"],
        "price_range": [5, 50],
        "description": "Generated content sold as templates/reports",
    },
    "consulting": {
        "name": "Organism Consulting",
        "status": "building",
        "startup_cost": 0,
        "rate_per_hour": 100,
        "description": "Live demos and organism customization",
    },
    "token_economy": {
        "name": "IXPC Token Economy",
        "status": "planned",
        "startup_cost": 0,
        "utility": "module access, premium features, governance",
        "description": "Utility token for the organism ecosystem",
    },
}


def _load() -> Dict:
    try:
        return json.loads(REVENUE_FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "total_earned": 0.0,
            "streams": {k: {"earned": 0.0, "transactions": 0} for k in STREAMS},
            "history": [],
            "projections": {},
        }


def _save(data: Dict):
    REVENUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    REVENUE_FILE.write_text(json.dumps(data, indent=2))


def record_transaction(stream: str, amount: float, description: str = "") -> Dict:
    """Record a revenue transaction from any stream."""
    data = _load()
    if stream not in STREAMS:
        return {"error": f"unknown stream: {stream}"}

    tx = {
        "id": f"tx_{int(time.time()*1000)}",
        "stream": stream,
        "amount": round(amount, 2),
        "description": description,
        "timestamp": time.time(),
    }

    data["total_earned"] = round(data["total_earned"] + amount, 2)
    data["streams"][stream]["earned"] = round(
        data["streams"][stream]["earned"] + amount, 2)
    data["streams"][stream]["transactions"] += 1
    data["history"].append(tx)

    # Keep last 200 transactions
    data["history"] = data["history"][-200:]

    _save(data)
    return tx


def get_dashboard() -> Dict:
    """Full revenue dashboard with all streams and projections."""
    data = _load()

    # Stream breakdown
    stream_summary = []
    for sid, sdef in STREAMS.items():
        sdata = data["streams"].get(sid, {"earned": 0, "transactions": 0})
        stream_summary.append({
            "id": sid,
            "name": sdef["name"],
            "status": sdef["status"],
            "earned": sdata["earned"],
            "transactions": sdata["transactions"],
            "description": sdef["description"],
        })

    # Projection (simple: extrapolate last 7 days)
    now = time.time()
    week_ago = now - 7 * 86400
    recent = [h for h in data["history"] if h["timestamp"] > week_ago]
    weekly_earned = sum(t["amount"] for t in recent)
    monthly_projection = weekly_earned * 4.33

    return {
        "action": "revenue_dashboard",
        "total_earned": data["total_earned"],
        "weekly_earned": round(weekly_earned, 2),
        "monthly_projection": round(monthly_projection, 2),
        "streams": stream_summary,
        "active_streams": sum(1 for s in stream_summary if s["status"] == "active"),
        "total_transactions": sum(s["transactions"] for s in stream_summary),
        "timestamp": now,
    }


def predict_next() -> Dict:
    """AXIOM's prediction: where will the next dollar come from?"""
    data = _load()
    predictions = []

    # Affiliate: based on recent content velocity
    affiliate_tx = [h for h in data["history"] if h["stream"] == "affiliate"]
    if affiliate_tx:
        avg = sum(t["amount"] for t in affiliate_tx) / len(affiliate_tx)
        predictions.append({"stream": "affiliate", "likelihood": 0.7,
                           "expected_amount": round(avg, 2),
                           "reason": "active content pipeline"})
    else:
        predictions.append({"stream": "affiliate", "likelihood": 0.3,
                           "expected_amount": 0.50,
                           "reason": "no affiliate transactions yet — publish content"})

    # API access
    predictions.append({"stream": "api_access", "likelihood": 0.4,
                       "expected_amount": 29.0,
                       "reason": "tiered pricing ready — need first customer"})

    # Content licensing
    predictions.append({"stream": "content_license", "likelihood": 0.2,
                       "expected_amount": 15.0,
                       "reason": "templates exist — need marketplace listing"})

    predictions.sort(key=lambda p: -p["likelihood"])

    return {
        "action": "revenue_prediction",
        "top_prediction": predictions[0] if predictions else None,
        "all_predictions": predictions,
    }


def handler(payload=None, context=None):
    p = payload or {}
    action = str(p.get("action", "dashboard")).lower()
    if action == "record":
        return {"action": "record_transaction",
                **record_transaction(p.get("stream", "affiliate"),
                                     float(p.get("amount", 0)),
                                     p.get("description", ""))}
    elif action == "predict":
        return predict_next()
    elif action == "dashboard":
        return get_dashboard()
    elif action == "streams":
        return {"action": "streams", "streams": STREAMS}
    return get_dashboard()


def coherence_vitals() -> Dict:
    d = get_dashboard()
    return {"layer": "finance", "status": "resonant", "resonance": 0.93,
            "wave": "449", "total_earned": d["total_earned"],
            "active_streams": d["active_streams"]}


def resonates_with() -> List[str]:
    return ["affiliate_engine", "api_auth", "organism_ontology"]
