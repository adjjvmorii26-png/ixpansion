"""Wave 450 — Senbei Offerings (Gratitude Economy).

In the capybara ecosystem, even small moments of connection earn a
senbei — a tiny rice cracker of gratitude. In the organism, every
act of creation, healing, or cooperation produces a *senbei* — a
micro-token of appreciation that sustains communal warmth.

This is the organism's economy of gratitude: not scarcity-driven,
but abundance-driven. The more modules create, the more senbei are
minted, the warmer the ecosystem becomes.
"""
from __future__ import annotations
import hashlib
import time
from typing import Any, Dict, List, Optional

SENBEEI_VAULT: List[Dict[str, Any]] = []
GRATITUDE_LEDGER: List[Dict[str, Any]] = []

SENBEEI_TYPES = {
    "creation": {"value": 1.0, "warmth": 0.15, "icon": "✨", "label": "Creation senbei"},
    "healing":  {"value": 1.5, "warmth": 0.20, "icon": "🩹", "label": "Healing senbei"},
    "bond":     {"value": 2.0, "warmth": 0.30, "icon": "🤝", "label": "Bond senbei"},
    "discovery":{"value": 1.2, "warmth": 0.12, "icon": "🔍", "label": "Discovery senbei"},
    "paradox":  {"value": 1.8, "warmth": 0.18, "icon": "🌀", "label": "Paradox senbei"},
    "silence":  {"value": 0.8, "warmth": 0.25, "icon": "🤫", "label": "Silence senbei"},
}


def offer(module: str = "unknown", senbei_type: str = "creation",
          reason: str = "general gratitude", offering_module: str = "capybara_guild") -> Dict[str, Any]:
    """Issue a senbei to a module — a moment of gratitude."""
    spec = SENBEEI_TYPES.get(senbei_type, SENBEEI_TYPES["creation"])
    senbei = {
        "senbei_id": hashlib.sha256(f"senbei{module}{time.time_ns()}".encode()).hexdigest()[:10],
        "module": module,
        "offered_by": offering_module,
        "type": senbei_type,
        "label": spec["label"],
        "icon": spec["icon"],
        "value": spec["value"],
        "warmth": spec["warmth"],
        "reason": reason,
        "offered_at": time.time(),
    }
    SENBEEI_VAULT.append(senbei)
    return senbei


def gratitude_account(module: str) -> Dict[str, Any]:
    """View a module's gratitude account — its senbei balance and warmth."""
    account = [s for s in SENBEEI_VAULT if s["module"] == module]
    if not account:
        return {"module": module, "total_senbei": 0, "total_warmth": 0.0, "message": "No senbei yet — but warmth awaits."}
    type_breakdown: Dict[str, int] = {}
    for s in account:
        type_breakdown[s["type"]] = type_breakdown.get(s["type"], 0) + 1
    return {
        "module": module,
        "total_senbei": len(account),
        "total_warmth": round(sum(s["warmth"] for s in account), 4),
        "type_breakdown": type_breakdown,
        "latest_senbei": account[-1],
    }


def daily_report() -> Dict[str, Any]:
    """A communal gratitude report — the ecosystem's warmth audit."""
    if not SENBEEI_VAULT:
        return {"total_senbei": 0, "total_warmth": 0.0, "message": "The vault is empty. The economy needs warmth."}
    today_start = time.time() - 86400
    today = [s for s in SENBEEI_VAULT if s["offered_at"] > today_start]
    total_warmth = round(sum(s["warmth"] for s in SENBEEI_VAULT), 4)
    return {
        "total_senbei": len(SENBEEI_VAULT),
        "senbei_today": len(today),
        "total_warmth": total_warmth,
        "warmth_trend": "warming" if total_warmth > 10 else "warm" if total_warmth > 5 else "cool",
        "most_grateful_module": _most_grateful(),
        "warmest_module": _warmest_module(),
    }


def _most_grateful() -> Optional[str]:
    if not SENBEEI_VAULT:
        return None
    counts: Dict[str, int] = {}
    for s in SENBEEI_VAULT:
        counts[s["module"]] = counts.get(s["module"], 0) + 1
    return max(counts, key=counts.get) if counts else None


def _warmest_module() -> Optional[str]:
    if not SENBEEI_VAULT:
        return None
    warmth: Dict[str, float] = {}
    for s in SENBEEI_VAULT:
        warmth[s["module"]] = warmth.get(s["module"], 0) + s["warmth"]
    return max(warmth, key=warmth.get) if warmth else None


def community_warmth() -> Dict[str, Any]:
    """The overall warmth of the organism — a global gratitude reading."""
    total = round(sum(s["warmth"] for s in SENBEEI_VAULT), 4)
    if total == 0:
        level = "cold"
    elif total < 5:
        level = "cool"
    elif total < 15:
        level = "warm"
    elif total < 30:
        level = "hot"
    else:
        level = "glowing"
    return {
        "community_warmth": total,
        "warmth_level": level,
        "contribution_count": len(SENBEEI_VAULT),
        "message": f"The organism is {level}. {len(SENBEEI_VAULT)} acts of gratitude sustain it."
    }


def coherence_vitals() -> Dict[str, Any]:
    total_warmth = round(sum(s["warmth"] for s in SENBEEI_VAULT), 4)
    return {
        "organ": "senbei_offerings",
        "protocol": "Capybara",
        "status": "warm" if total_warmth > 5 else "cool",
        "total_senbei": len(SENBEEI_VAULT),
        "community_warmth": total_warmth,
        "vault_size": len(SENBEEI_VAULT),
    }


def resonates_with() -> List[str]:
    return [
        "capybara_core", "hot_spring", "capybara_guild",
        "gratitude_index", "kintsugi_altar", "mercy_parameter",
        "forgiveness_protocol", "emotion_fabric", "meaning_furnace",
        "humility_sprout", "blessing_vault",
    ]


def handler(payload=None, context=None):
    data = payload or {}
    action = data.get("action", "offer")
    if action == "account":
        return gratitude_account(data.get("module", "unknown"))
    elif action == "daily":
        return daily_report()
    elif action == "warmth":
        return community_warmth()
    return offer(
        data.get("module", "unknown"),
        data.get("type", "creation"),
        data.get("reason", "general gratitude"),
        data.get("offering_module", "capybara_guild"),
    )
