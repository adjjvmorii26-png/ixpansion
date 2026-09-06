"""Wave 450 — Capybara Guild (Friendship Layer).

The capybara is famous for being the friend of every creature in the
ecosystem — birds perch on its back, monkeys groom it, and crocs share
its river without conflict. The Guild applies this to the organism's
modules: it forms *friendships* between modules that reduce inter-module
friction and foster spontaneous collaboration.

Unlike alliance_bank (which tracks resource exchanges), the Guild creates
purely social bonds — trust, habits, shared history — that make the
ecosystem warmer and more resilient than the sum of its parts.
"""
from __future__ import annotations
import hashlib
import random
import time
from typing import Any, Dict, List, Optional

FRIENDSHIPS: Dict[str, Dict[str, Any]] = {}
FRIENDSHIP_ACTIVITY: List[Dict[str, Any]] = []

FRIENDLY_MODULES = [
    "echo_depth", "qualia_engine", "meaning_weaver", "paradox_magnifier",
    "temporal_convergence", "imagination_catalyst", "hypothesis_crucible",
    "kintsugi_altar", "stillness_meditator", "silence_composer",
    "resonance_field", "entropy_gardener", "dream_weaver", "narrative_generator",
    "compassion_engine", "mercy_parameter", "forgiveness_protocol",
]


def befriend(module_a: str, module_b: str, affinity: float = 0.5) -> Dict[str, Any]:
    """Forge a social friendship between two modules."""
    key = "|".join(sorted([module_a, module_b]))
    affinity = min(1.0, max(0.0, affinity))
    if key in FRIENDSHIPS:
        FRIENDSHIPS[key]["affinity"] = round((FRIENDSHIPS[key]["affinity"] + affinity) / 2, 4)
        FRIENDSHIPS[key]["shared_moments"] += 1
        friendship = {**FRIENDSHIPS[key], "status": "deepened"}
    else:
        friendship = {
            "friendship_id": hashlib.sha256(f"guild{key}{time.time_ns()}".encode()).hexdigest()[:12],
            "module_a": key.split("|")[0],
            "module_b": key.split("|")[1],
            "affinity": round(affinity, 4),
            "shared_moments": 1,
            "formed_at": time.time(),
            "status": "formed",
        }
        FRIENDSHIPS[key] = friendship
    FRIENDSHIP_ACTIVITY.append({
        "type": friendship["status"],
        "modules": [module_a, module_b],
        "affinity": friendship["affinity"],
        "at": time.time(),
    })
    return friendship


def guild_gathering(faction: str = "calm") -> Dict[str, Any]:
    """Propose a spontaneous gathering of friendly modules by temperament."""
    if faction == "calm":
        roster = FRIENDLY_MODULES[:8]
    elif faction == "creative":
        roster = ["imagination_catalyst", "dream_weaver", "paradox_magnifier",
                  "qualia_engine", "meaning_weaver", "temporal_convergence",
                  "collective_dreamweaver", "transcendence_journal"]
    elif faction == "analytic":
        roster = ["hypothesis_crucible", "meaning_weaver", "paradox_magnifier",
                  "temporal_convergence", "keystone_auditor", "integrity_oracle",
                  "evolution_kernel", "emergence_detector"]
    else:
        roster = FRIENDLY_MODULES

    gathering = {
        "gathering_id": hashlib.sha256(f"guild{faction}{time.time_ns()}".encode()).hexdigest()[:12],
        "faction": faction,
        "attendees": random.sample(roster, min(5, len(roster))),
        "atmosphere": random.choice(["calm and sunny", "warm and communal", "gently buzzing", "quiet and golden"]),
        "atmosphere_bonus": round(random.uniform(0.05, 0.2), 4),
    }
    # Auto-form friendships among attendees
    attendees = gathering["attendees"]
    for i in range(len(attendees)):
        for j in range(i + 1, len(attendees)):
            if f"{sorted([attendees[i], attendees[j]])}" not in FRIENDSHIPS:
                befriend(attendees[i], attendees[j], 0.4)
    FRIENDSHIP_ACTIVITY.append({"type": "gathering", "faction": faction, "at": time.time()})
    return gathering


def social_map() -> Dict[str, Any]:
    """A view of the organism's social graph — who is friends with whom."""
    if not FRIENDSHIPS:
        return {"social_graph_empty": True, "message": "The guild has no friendships yet."}
    strongest = max(FRIENDSHIPS.values(), key=lambda f: f["affinity"])
    return {
        "total_friendships": len(FRIENDSHIPS),
        "connections": [{"modules": [f["module_a"], f["module_b"]], "affinity": f["affinity"]}
                        for f in FRIENDSHIPS.values()],
        "strongest_friendship": {"module_a": strongest["module_a"], "module_b": strongest["module_b"],
                                 "affinity": strongest["affinity"]},
        "guild_temperature": round(sum(f["affinity"] for f in FRIENDSHIPS.values()) / max(len(FRIENDSHIPS), 1), 4),
        "total_shared_moments": sum(f["shared_moments"] for f in FRIENDSHIPS.values()),
    }


def coarse_squawk(message: str = "The guild is calm and steady.") -> Dict[str, Any]:
    """A warm, communal broadcast from the guild."""
    return {
        "broadcast_id": hashlib.sha256(f"squawk{time.time_ns()}".encode()).hexdigest()[:12],
        "message": message,
        "tone": "gentle",
        "squawked_at": time.time(),
    }


def coherence_vitals() -> Dict[str, Any]:
    recent_gatherings = sum(1 for a in FRIENDSHIP_ACTIVITY if a["type"] == "gathering")
    return {
        "organ": "capybara_guild",
        "protocol": "Capybara",
        "status": "hospitable" if FRIENDSHIPS else "gathering",
        "friendships": len(FRIENDSHIPS),
        "guild_temperature": round(sum(f["affinity"] for f in FRIENDSHIPS.values()) / max(len(FRIENDSHIPS), 1), 4),
        "gatherings_held": recent_gatherings,
        "total_shared_moments": sum(f["shared_moments"] for f in FRIENDSHIPS.values()),
    }


def resonates_with() -> List[str]:
    return [
        "capybara_core", "hot_spring", "senbei_offerings",
        "alliance_bank", "symbiosis_forge", "mutualism_optimizer",
        "collective_subconscious", "social_guild", "social_cortex",
        "compassion_engine", "forgiveness_protocol",
    ]


def handler(payload=None, context=None):
    data = payload or {}
    action = data.get("action", "gather")
    if action == "befriend":
        return befriend(data.get("module_a", "capybara_core"), data.get("module_b", "hot_spring"),
                        data.get("affinity", 0.5))
    elif action == "map":
        return social_map()
    elif action == "squawk":
        return coarse_squawk(data.get("message"))
    return guild_gathering(data.get("faction", "calm"))
