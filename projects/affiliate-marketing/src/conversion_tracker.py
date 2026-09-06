"""
Conversion Tracker — tracks affiliate clicks, conversions, and revenue.

AXIOM's domain: every click is measured, every conversion is logged,
every dollar is accounted for. $0 start = zero ad spend, all organic.

Tracking methods:
- UTM parameters on affiliate links
- Click event logging
- Conversion attribution
- EPC (earnings per click) calculation
"""
from __future__ import annotations
import hashlib
import json
import time
from pathlib import Path
from typing import Dict, List

DATA_DIR = Path(__file__).parent.parent / "data"
CLICKS_FILE = DATA_DIR / "clicks.json"
CONVERSIONS_FILE = DATA_DIR / "conversions.json"
CAMPAIGNS_FILE = DATA_DIR / "campaigns.json"


def _load(path: Path) -> Dict:
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {"events": [], "summary": {}}


def _save(path: Path, data: Dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def track_click(source: str, product: str, campaign: str = "default") -> Dict:
    """Record an affiliate click with UTM parameters."""
    data = _load(CLICKS_FILE)
    click = {
        "id": f"clk_{int(time.time()*1000)}",
        "source": source,
        "product": product,
        "campaign": campaign,
        "timestamp": time.time(),
        "utm_source": source,
        "utm_medium": "affiliate",
        "utm_campaign": campaign,
    }
    data["events"].append(click)
    data["summary"][source] = data["summary"].get(source, 0) + 1
    _save(CLICKS_FILE, data)
    return {"action": "click_tracked", **click}


def track_conversion(click_id: str, revenue: float, commission: float) -> Dict:
    """Record a conversion (sale) from an affiliate link."""
    data = _load(CONVERSIONS_FILE)
    conversion = {
        "id": f"conv_{int(time.time()*1000)}",
        "click_id": click_id,
        "revenue": revenue,
        "commission": commission,
        "timestamp": time.time(),
    }
    data["events"].append(conversion)
    # Update summary
    s = data["summary"]
    s["total_conversions"] = s.get("total_conversions", 0) + 1
    s["total_revenue"] = s.get("total_revenue", 0) + revenue
    s["total_commission"] = s.get("total_commission", 0) + commission
    s["conversion_rate"] = round(
        s["total_conversions"] / max(1, _load(CLICKS_FILE)["summary"].get("total", len(_load(CLICKS_FILE)["events"]))),
        4
    )
    _save(CONVERSIONS_FILE, data)
    return {"action": "conversion_tracked", **conversion}


def get_dashboard() -> Dict:
    """Get the full affiliate dashboard metrics."""
    clicks = _load(CLICKS_FILE)
    conversions = _load(CONVERSIONS_FILE)
    cs = conversions.get("summary", {})

    total_clicks = len(clicks.get("events", []))
    total_conversions = cs.get("total_conversions", 0)
    total_commission = cs.get("total_commission", 0)

    return {
        "action": "affiliate_dashboard",
        "total_clicks": total_clicks,
        "total_conversions": total_conversions,
        "total_revenue": cs.get("total_revenue", 0),
        "total_commission": round(total_commission, 2),
        "conversion_rate": round(total_conversions / max(1, total_clicks), 4),
        "epc": round(total_commission / max(1, total_clicks), 4),
        "clicks_by_source": clicks.get("summary", {}),
        "period": "all_time",
    }


def create_campaign(name: str, products: List[str], platforms: List[str]) -> Dict:
    """Create a new affiliate campaign."""
    data = _load(CAMPAIGNS_FILE)
    campaign = {
        "name": name,
        "products": products,
        "platforms": platforms,
        "created": time.time(),
        "status": "active",
        "budget": 0,  # $0 start
    }
    data.setdefault("campaigns", []).append(campaign)
    _save(CAMPAIGNS_FILE, data)
    return {"action": "campaign_created", **campaign}


def handler(payload: Dict = None, context: Dict = None) -> Dict:
    p = payload or {}
    action = str(p.get("action", "dashboard")).lower()
    if action == "click":
        return {"action": "track_click", **track_click(
            p.get("source", "unknown"), p.get("product", "unknown"),
            p.get("campaign", "default"))}
    elif action == "conversion":
        return {"action": "track_conversion", **track_conversion(
            p.get("click_id", ""), float(p.get("revenue", 0)),
            float(p.get("commission", 0)))}
    elif action == "campaign":
        return {"action": "create_campaign", **create_campaign(
            p.get("name", f"campaign_{int(time.time())}"),
            p.get("products", []), p.get("platforms", []))}
    elif action == "dashboard":
        return get_dashboard()
    return {"action": "conversion_tracker", "status": "active"}


def coherence_vitals() -> Dict:
    d = get_dashboard()
    return {"layer": "analytics", "status": "resonant", "resonance": 0.88,
            "wave": "449", "clicks": d["total_clicks"],
            "conversions": d["total_conversions"]}


def resonates_with() -> List[str]:
    return ["content_engine", "publishing_adapter", "optimization_engine"]
