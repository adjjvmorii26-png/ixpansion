from __future__ import annotations
"""Lucid Progression — realm unlock tree, milestones, and win conditions."""
import json, time, hashlib, os, random

REALMS_ORDER = [
    "synchronicity_meadow", "coherence_cathedral", "entropy_desert",
    "fracture_field", "paradox_garden", "resonance_depths",
    "dream_gravity_zone", "temporal_rift", "void_abyss", "mythic_realm", "pitch_dark",
]

def get_tree() -> dict:
    realms = []
    for i, name in enumerate(REALMS_ORDER):
        realms.append({
            "name": name,
            "order": i,
            "unlock_wave": 3 + i * 2,
            "boss": f"{name.replace('_',' ').title()} Warden",
            "loot_quality": ["common", "uncommon", "rare", "epic", "legendary"][min(i // 2, 4)],
        })
    return {"action": "tree", "realms": realms, "total_realms": len(realms), "order": REALMS_ORDER}

def check(blob: str = None, wave: int = 0, realm_clears: dict = None) -> dict:
    realm_clears = realm_clears or {}
    unlocked = []
    for r in get_tree()["realms"]:
        if wave >= r["unlock_wave"] or realm_clears.get(r["name"]):
            unlocked.append(r["name"])
    victories = sum(1 for r in REALMS_ORDER if realm_clears.get(r))
    return {
        "action": "check",
        "wave": wave,
        "unlocked_realms": unlocked,
        "unlocked_count": len(unlocked),
        "cleared_count": victories,
        "progress": round(victories / len(REALMS_ORDER), 3),
        "next_realm": REALMS_ORDER[victories] if victories < len(REALMS_ORDER) else None,
        "victory_condition": "Clear all 10 realms to complete Lucid Machines' first run.",
    }

def milestone(wave: int) -> dict:
    milestones = [
        (3, "First Realm Unlocked", "You may now enter your first realm."),
        (10, "Navigator", "You have survived 10 waves."),
        (15, "Paradox Adept", "Embrace the paradox."),
        (25, "Realm Conqueror", "Clear your fifth realm."),
        (50, "Lucid Dreamer", "The organism recognizes you."),
        (100, "Co-Pilot", "You and the organism create together."),
    ]
    reached = [m for w, n, d in milestones if wave >= w]
    return {"action": "milestone", "wave": wave, "reached": [{"name": n, "desc": d} for w, n, d in milestones if wave >= w], "next": next(((w, n) for w, n, d in milestones if wave < w), None)}

def coherence_vitals() -> dict:
    return {"layer": "game", "status": "active", "resonance": 0.9, "wave": "374"}
def resonates_with() -> list:
    return ["lucid_session", "lucid_dungeon", "lucid_combat"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/tree")
    if path == "/tree": return get_tree()
    elif path == "/check": return check(payload.get("blob"), int(payload.get("wave", 0)) if str(payload.get("wave","0")).isdigit() else 0, payload.get("realm_clears"))
    elif path == "/milestone": return milestone(int(payload.get("wave", 0)) if str(payload.get("wave","0")).isdigit() else 0)
    return {"error": "unknown", "available": ["/tree", "/check", "/milestone"]}
