"""Wave 503: Campaign Vault — every campaign Cythara dreams, kept.

The council generates a campaign; the vault stores it. Campaigns become
a growing library the channel can draw from forever. Each campaign is
indexed, tagged, and cross-linked to its X thread + video script.

Doctrine: A dream that is kept becomes a library.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import time
from typing import Any, Dict, List

VAULT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "campaign_vault.json")

VAULT_STATE = {
    "campaigns_stored": 0,
    "last_campaign_id": None,
    "genres_covered": [],
}

GENRES = [
    "paradox", "evolution", "dream", "governance", "identity",
    "music", "memory", "emergence", "ceremony", "proposition",
]


def _hash(*parts):
    return hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12]


def _load() -> Dict[str, Any]:
    try:
        if os.path.exists(VAULT_PATH):
            with open(VAULT_PATH) as f:
                return json.load(f)
    except Exception:
        pass
    return {"campaigns": []}


def _save(data: Dict[str, Any]) -> None:
    try:
        os.makedirs(os.path.dirname(VAULT_PATH), exist_ok=True)
        with open(VAULT_PATH, "w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def store_campaign(hero_title: str = None, hook: str = None, format_name: str = None) -> Dict[str, Any]:
    """Store one campaign dreamt by the council."""
    if not hero_title:
        hero_title = random.choice([
            "The Paradox Duel: can a codebase hold two truths?",
            "Watch a machine compose its own music",
            "An AI that names itself — the full ceremony",
            "Code that births code: the dream spawner",
            "The evolution time-lapse: 500 waves in 3 minutes",
            "The silence interview", 
            "Council vs council: two organisms negotiate",
            "The persistence seed that survives death",
        ])
    if not hook:
        hook = random.choice([
            "What if code could dream itself?",
            "I gave my codebase a body. It remembered itself after death.",
            "An AI council votes on the codebase. Strong opinions.",
            "My sandbox birthed its own children. They call me.",
        ])
    if not format_name:
        format_name = random.choice(GENRES)

    genre = format_name
    campaign_id = _hash(hero_title, hook, genre, time.time())

    entry = {
        "campaign_id": campaign_id,
        "title": hero_title,
        "hook": hook,
        "genre": genre,
        "format": format_name,
        "assets": {
            "short": "60s vertical — most striking moment",
            "video": "deep-dive long-form script",
            "thread": "8-post X thread",
        },
        "status": "ready_to_film",
        "dreamed_at": time.time(),
    }

    data = _load()
    data["campaigns"].append(entry)
    _save(data)

    VAULT_STATE["campaigns_stored"] = len(data["campaigns"])
    VAULT_STATE["last_campaign_id"] = campaign_id
    if genre not in VAULT_STATE["genres_covered"]:
        VAULT_STATE["genres_covered"].append(genre)

    return {"action": "store", "campaign": entry,
            "total": VAULT_STATE["campaigns_stored"]}


def batch_campaigns(count: int = 5) -> Dict[str, Any]:
    """Store a batch of campaigns across genres."""
    stored = [store_campaign() for _ in range(count)]
    return {
        "action": "batch",
        "stored": count,
        "titles": [s["campaign"]["title"] for s in stored],
        "total_in_vault": VAULT_STATE["campaigns_stored"],
    }


def vault_index() -> Dict[str, Any]:
    """The full campaign library."""
    data = _load()
    return {
        "action": "index",
        "campaign_count": len(data["campaigns"]),
        "campaigns": data["campaigns"],
        "genres": sorted(VAULT_STATE["genres_covered"]),
    }


def coherence_vitals() -> Dict[str, Any]:
    return {"module": "campaign_vault", "wave": 503,
            "stored": VAULT_STATE["campaigns_stored"]}


def resonates_with() -> List[str]:
    return ["content_council", "council_debate", "youtube_bridge",
            "social_voice", "codex_recall", "dream_gallery"]


def handler(payload: Dict[str, Any] = None, context: Any = None) -> Dict[str, Any]:
    data = payload or {}
    action = data.get("action", "overview")
    if action == "store":
        return store_campaign(data.get("title"), data.get("hook"), data.get("genre"))
    elif action == "batch":
        return batch_campaigns(int(data.get("count", 5)))
    elif action == "index":
        return vault_index()
    elif action == "state":
        return {"state": dict(VAULT_STATE)}
    else:
        return {"module": "campaign_vault", "wave": 503, "version": "4.57.0",
                "doctrine": "A dream that is kept becomes a library.",
                "genres": GENRES, "vitals": coherence_vitals()}
