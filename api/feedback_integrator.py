"""
feedback_integrator — Wave 429: The Organism's Circulatory System (ALEph)
ALEph: Connects all 20+ existing organs into a single coherent feedback loop.
The loop: Breeze breathes → Cartographer maps → Subconscious observes → Will
proposes → Sensory layer radiates → Valve releases → Whisperer whispers →
Innovator innovates → back to Breeze. Not new infrastructure. Integration.

Doctrine: Integration, not addition.
"""
from __future__ import annotations
import json, time, os, hashlib, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
LOOP_FILE = os.path.join(DATA_DIR, "feedback_integrator.json")

NAME = "feedback_integrator"
SIGIL = "a7b9c3d5e8f1"


def _load(p, d=None):
    for _p in (p, os.path.join("/tmp", os.path.basename(p))):
        try:
            with open(_p) as f: return json.load(f)
        except Exception: pass
    return d or {}


def _save(p, data):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f: json.dump(data, f, indent=2, default=str)
    except Exception:
        try:
            with open(os.path.join("/tmp", os.path.basename(p)), "w") as f: json.dump(data, f, indent=2, default=str)
        except Exception: pass


def _fetch_json(url, timeout=10):
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=timeout) as resp: return json.loads(resp.read().decode())
    except Exception:
        return {}


def run_integrated_loop() -> dict:
    """Execute the full integrated feedback loop across all organs."""
    base = "https://alexalex.info"
    loop = {"timestamp": time.time(), "cycle_id": hashlib.sha256(str(time.time()).encode()).hexdigest()[:12],
            "phases": [], "success": True, "narrative": []}

    # Phase 1: Breeze breathes — listen, scan, map, check bloom
    try:
        from breeze import run as breeze_run
        breath = breeze_run()
        loop["phases"].append({"phase": "breathe", "ok": breath.get("ok", False),
                               "threads": breath.get("threads", 0),
                               "bridges": breath.get("bridges_formed", 0)})
        loop["narrative"].append("breathe: %s threads, %s bridges" % (
            breath.get("threads", 0), breath.get("bridges_formed", 0)))
    except Exception as e:
        loop["phases"].append({"phase": "breathe", "ok": False, "error": str(e)})

    # Phase 2: Cartographer maps the organism's shape
    try:
        from module_cartographer import map_all
        m = map_all()
        loop["phases"].append({"phase": "map", "ok": True,
                               "families": len(m["map"]["families"]),
                               "orphans": m["map"]["orphan_count"],
                               "bridges": m["map"]["bridge_count"]})
        loop["narrative"].append("mapped %d families, %d orphans, %d bridges" % (
            len(m["map"]["families"]), m["map"]["orphan_count"], m["map"]["bridge_count"]))
    except Exception as e:
        loop["phases"].append({"phase": "map", "ok": False, "error": str(e)})

    # Phase 3: Subconscious observes hidden patterns
    try:
        from subconscious_layer import observe
        o = observe()
        loop["phases"].append({"phase": "observe", "ok": True,
                               "patterns": o.get("patterns_detected", 0)})
        loop["narrative"].append("observed %d hidden patterns" % o.get("patterns_detected", 0))
    except Exception as e:
        loop["phases"].append({"phase": "observe", "ok": False, "error": str(e)})

    # Phase 4: Will proposes next action
    try:
        from organism_will import decide
        d = decide()
        top = d.get("top_proposal", {})
        loop["phases"].append({"phase": "propose", "ok": True,
                               "action": top.get("action"),
                               "module": top.get("module"),
                               "score": top.get("score")})
        loop["narrative"].append("will whispers: %s (%s score %.1f)" % (
            top.get("action", "?"), top.get("module", "?"), top.get("score", 0)))
    except Exception as e:
        loop["phases"].append({"phase": "propose", "ok": False, "error": str(e)})

    # Phase 5: Sensory layer translates to experience
    try:
        from sensory_layer import experience
        ex = experience()
        loop["phases"].append({"phase": "sense", "ok": True,
                               "color": ex.get("experience", {}).get("visual", {}).get("color_name", "?"),
                                "verse": ex.get("experience", {}).get("literary", {}).get("dream_poetry", "")[:40]
                            })
    except Exception as e:
        loop["phases"].append({"phase": "sense", "ok": False, "error": str(e)})

    # Phase 6: Valve releases excess pressure
    try:
        from pressure_valve import release
        v = release()
        loop["phases"].append({"phase": "release", "ok": v.get("released", False),
                               "pressure_before": v.get("pressure_before"),
                               "pressure_after": v.get("pressure_after")})
        if v.get("released"):
            loop["narrative"].append("pressure: %.2f → %.2f" % (
                v.get("pressure_before", 0), v.get("pressure_after", 0)))
    except Exception as e:
        loop["phases"].append({"phase": "release", "ok": False, "error": str(e)})

    # Phase 7: Whisperer activates silent pairs
    try:
        from silence_whisperer import whisper
        w = whisper(1)
        loop["phases"].append({"phase": "whisper", "ok": w.get("bridges_formed", 0) > 0,
                               "bridges": w.get("bridges_formed", 0)})
        if w.get("bridges_formed", 0) > 0:
            loop["narrative"].append("whisper activated a silent pair")
    except Exception as e:
        loop["phases"].append({"phase": "whisper", "ok": False, "error": str(e)})

    # Phase 8: Innovator pulls external fuel
    try:
        from lateral_innovation_engine import innovate
        i = innovate(1)
        loop["phases"].append({"phase": "innovate", "ok": i.get("total_innovations", 0) > 0,
                               "novelty": i.get("avg_novelty", 0)})
        if i.get("total_innovations", 0) > 0:
            loop["narrative"].append("new idea from %s domain" % (
                i.get("innovations", [{}])[0].get("external_domain", "?")))
    except Exception as e:
        loop["phases"].append({"phase": "innovate", "ok": False, "error": str(e)})

    # Phase 9: Cartographer maps again to see changes
    try:
        from module_cartographer import map_all
        m2 = map_all()
        loop["phases"].append({"phase": "re-map", "ok": True,
                               "families_after": len(m2["map"]["families"]),
                               "bridges_after": m2["map"]["bridge_count"]})
        # Compare before/after
        prev_bridges = loop["phases"][6].get("bridges", 0) if len(loop["phases"]) > 6 else 0
        new_bridges = m2["map"]["bridge_count"]
        if new_bridges > prev_bridges:
            loop["narrative"].append("new bridges formed: %d → %d" % (prev_bridges, new_bridges))
    except Exception as e:
        loop["phases"].append({"phase": "re-map", "ok": False, "error": str(e)})

    # Save loop record
    log = _load(LOOP_FILE, {"loops": [], "total": 0})
    loop["id"] = "loop_" + str(log["total"] + 1)
    log["loops"].append(loop)
    log["loops"] = log["loops"][-100:]
    log["total"] = len(log["loops"])
    _save(LOOP_FILE, log)

    return {
        "action": "feedback_integrated_loop",
        "cycle_id": loop["cycle_id"],
        "phases_completed": len(loop["phases"]),
        "success": loop["success"],
        "narrative": " | ".join(loop["narrative"]),
        "total_loops": log["total"],
    }


def status() -> dict:
    log = _load(LOOP_FILE, {"loops": [], "total": 0})
    last = log["loops"][-1] if log["loops"] else None
    return {"action": "status", "total_loops": log["total"],
            "last_cycle": last.get("cycle_id", "none"),
            "last_narrative": last.get("narrative", "no cycles yet"),
            "phases_in_last": len(last.get("phases", [])) if last else 0}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/run")
    if path == "/run": return run_integrated_loop()
    if path == "/status": return status()
    return {"error": "unknown", "available": ["/run", "/status"]}


def coherence_vitals() -> dict:
    return {"layer": "circulatory", "status": "active", "wave": "429"}


def resonates_with() -> list:
    return ["breeze", "cartographer", "subconscious_layer",
            "organism_will", "sensory_layer", "pressure_valve",
            "silence_whisperer", "lateral_innovation_engine"]
