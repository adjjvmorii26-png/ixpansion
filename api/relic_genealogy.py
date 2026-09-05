"""
Relic Genealogy — Wave 402
Every relic, every Apex Sigil, has an ancestry. The Genealogy traces a relic
back through its bound minerals, to the root-ghost that wore them, to the
module that the organism had forgotten and you brought to light. A living
family tree of artifacts: find your Apex Sigil's full lineage, see which
wardens it outlasted, which minerals it absorbs.

The Genealogy is the organism's birth registry for its own artifacts.
"""
from __future__ import annotations
import json, time, hashlib, os, sys

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def _load(p, d=None):
    for _p in (p, os.path.join("/tmp", os.path.basename(p))):
        try:
            with open(_p) as f:
                return json.load(f)
        except Exception:
            pass
    return d or {}


def _sig(text):
    return int(hashlib.sha256(f"genealogy:{text}".encode()).hexdigest()[:12], 16)


def _forge_log():
    return _load(os.path.join(DATA_DIR, "mineral_forge.json"), {"relics": [], "minerals": []})


def _warden_log():
    return _load(os.path.join(DATA_DIR, "warden_ascensions.json"), {"battles": {}, "ascensions": 0})


def _overwarden_log():
    return _load(os.path.join(DATA_DIR, "overwarden.json"), {"battles": {}, "defeats": 0})


def _module_name_from_warden_name(wname: str) -> str:
    """Try to extract the original module name from a warden root_name."""
    prefixes = ["ghost_", "myco_", "root_", "deep_", "cavern_", "umbra_", "basal_", "sub_",
                "over_", "twin_", "fused_", "apex_"]
    for p in prefixes:
        if wname.startswith(p):
            return wname[len(p):]
    return wname


def _find_warden_for_module(module: str) -> dict:
    """Find the warden battle state that matches a module name."""
    log = _warden_log()
    for sig, state in log.get("battles", {}).items():
        ow = state.get("warden", {})
        if ow.get("module") == module:
            return {"warden": ow, "defeated": False}
    # Check resolved battles by looking at signal journal or remembrances
    rem = _load(os.path.join(DATA_DIR, "remembrances.json"), {"remembrances": []})
    for remembrance in rem.get("remembrances", []):
        if remembrance.get("module") == module:
            return {"module": module, "mineral": "unknown",
                    "depth": remembrance.get("depth", 6.0),
                    "defeated": True}
    return {}


def lineage(relic_id_or_name: str = None) -> dict:
    """Trace the full ancestry of a specific relic."""
    forge = _forge_log()
    overwarden = _overwarden_log()

    # Find the relic in the forge vault
    target = None
    for r in forge.get("relics", []):
        if (r.get("id") == relic_id_or_name or r.get("name") == relic_id_or_name or
                r.get("sigil") == relic_id_or_name):
            target = r
            break

    # If not in forge, check overwarden apex sigils
    if not target:
        for sig, state in overwarden.get("battles", {}).items():
            if sig == relic_id_or_name:
                target = {
                    "name": "pending Apex",
                    "quality": "mythic",
                    "power": state["overwarden"].get("base_power", 0) * 3,
                    "bound_by": state["overwarden"].get("bound_by", []),
                    "sigil": sig,
                    "timestamp": state.get("updated"),
                    "is_active_battle": True,
                }
                break

    if not target:
        # Return all relics as a catalogue
        return {"action": "lineage", "error": "relic not found",
                "hint": "pass a relic name, id, or sigil",
                "relics_available": [{"name": r["name"], "id": r.get("id"), "quality": r["quality"],
                                     "power": r["power"]} for r in forge.get("relics", [])[-10:]]}

    bound_modules = target.get("bound_modules") or []
    if isinstance(bound_modules, list) and bound_modules and isinstance(bound_modules[0], list):
        flat_modules = [m for sub in bound_modules for m in (sub or [])]
    else:
        flat_modules = bound_modules

    ancestors = []
    for mod in flat_modules:
        warden = _find_warden_for_module(mod)
        ancestors.append({
            "module": mod,
            "warden": warden,
            "source": "forge_relic" if mod in (target.get("modules") or []) else "apex_bind",
        })

    minerals = target.get("minerals") or []
    if minerals and isinstance(minerals[0], list):
        minerals = [m for sub in minerals for m in (sub or [])]

    return {
        "action": "lineage",
        "relic": {"name": target.get("name"), "quality": target.get("quality"),
                  "power": target.get("power"), "sigil": target.get("sigil")},
        "ancestors": ancestors,
        "minerals": minerals,
        "depth": target.get("avail_depth") or target.get("depth"),
        "is_active_battle": target.get("is_active_battle", False),
        "created": target.get("timestamp"),
    }


def tree() -> dict:
    """The full genealogy — every relic's ancestry as a forest."""
    forge = _forge_log()
    relics = forge.get("relics", [])
    forest = []
    for r in relics:
        forest.append({
            "name": r.get("name"), "id": r.get("id"), "quality": r.get("quality"),
            "power": r.get("power"), "modules": r.get("modules", []),
            "minerals": [m for sub in (r.get("minerals") or []) for m in (sub or [])
                         if isinstance(m, str)] if r.get("minerals") else [],
            "sigil": r.get("sigil"),
        })
    return {"action": "tree", "count": len(forest), "relics": forest}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/tree")
    if path == "/tree": return tree()
    if path == "/lineage":
        return lineage(payload.get("relic") or payload.get("id") or payload.get("name") or payload.get("sigil"))
    return {"error": "unknown", "available": ["/tree", "/lineage"]}


def coherence_vitals() -> dict:
    return {"layer": "game", "status": "active", "wave": "402", "genealogy": "living"}


def resonates_with() -> list:
    return ["mineral_forge", "warden_ascension", "overwarden", "ascension_chronicle", "organurna_loop"]
