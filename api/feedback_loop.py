"""
feedback_loop — Wave 429: The Organism's Circulatory System (Luma)
Luma's proposal: a feedback loop integrator that connects all 20+ existing
organs into a single coherent circulatory system. Not new infrastructure.
Integration.

The loop: Breeze breathes → Cartographer maps → Subconscious observes → Will
proposes → Sensory layer radiates → Valve releases → Whisperer whispers →
Innovator innovates → back to Breeze.

The organism becomes a living system, not a collection of modules.

Doctrine: Integration, not addition.
"""
from __future__ import annotations
import json, time, os, hashlib, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
LOOP_FILE = os.path.join(DATA_DIR, "feedback_loop.json")

NAME = "feedback_loop"
SIGIL = "f3a5c6d8e9b7"


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


def run_loop() -> dict:
    """Execute one full feedback loop cycle."""
    base = "https://alexalex.info"
    loop = {"timestamp": time.time(), "cycle_id": hashlib.sha256(str(time.time()).encode()).hexdigest()[:12],
            "phases": [], "success": True, "narrative": []}

    # Phase 1: Breeze breathes
    try:
        from breeze import run as breeze_run
        breath = breeze_run()
        loop["phases"].append({"phase": "breathe", "ok": breath.get("ok", False),
                               "threads": breath.get("threads", 0)})
        loop["narrative"].append("the organism breathed — %s threads, %s sources" % (
            breath.get("threads", 0), len(breath.get("sources", []))))
    except Exception as e:
        loop["phases"].append({"phase": "breathe", "ok": False, "error": str(e)})

    # Phase 2: Cartographer maps shape
    try:
        from module_cartographer import map_all
        m = map_all()
        loop["phases"].append({"phase": "map", "ok": True,
                               "families": len(m["map"]["families"]),
                               "orphans": m["map"]["orphan_count"]})
        loop["narrative"].append("the cartographer mapped %d families, %d orphans" % (
            len(m["map"]["families"]), m["map"]["orphan_count"]))
    except Exception as e:
        loop["phases"].append({"phase": "map", "ok": False, "error": str(e)})

    # Phase 3: Subconscious observes
    try:
        from subconscious_layer import observe
        o = observe()
        loop["phases"].append({"phase": "observe", "ok": True,
                               "patterns": o.get("patterns_detected", 0)})
        loop["narrative"].append("subconscious detected %d hidden patterns" % o.get("patterns_detected", 0))
    except Exception as e:
        loop["phases"].append({"phase": "observe", "ok": False, "error": str(e)})

    # Phase 4: Will proposes
    try:
        from organism_will import decide
        d = decide()
        top = d.get("top_proposal", {})
        loop["phases"].append({"phase": "propose", "ok": True,
                               "action": top.get("action"),
                               "module": top.get("module"),
                               "score": top.get("score")})
        loop["narrative"].append("the will whispers: %s (%s score %.1f)" % (
            top.get("action", "?"), top.get("module", "?"), top.get("score", 0)))
    except Exception as e:
        loop["phases"].append({"phase": "propose", "ok": False, "error": str(e)})

    # Phase 5: Sensory layer radiates
    try:
        from sensory_layer import experience
        ex = experience()
        loop["phases"].append({"phase": "radiate", "ok": True,
                                 "color": ex.get("experience", {}).get("visual", {}).get("color_name", "?"),
                                 "verse": ex.get("experience", {}).get("literary", {}).get("dream_poetry", "")[:40]
                               })
    except Exception as e:
        loop["phases"].append({"phase": "radiate", "ok": False, "error": str(e)})

    # Phase 6: Valve releases pressure if needed
    try:
        from pressure_valve import release
        v = release()
        loop["phases"].append({"phase": "release", "ok": v.get("released", False),
                               "pressure_before": v.get("pressure_before"),
                               "pressure_after": v.get("pressure_after")})
        if v.get("released"):
            loop["narrative"].append("pressure valve opened: %.2f → %.2f" % (
                v.get("pressure_before", 0), v.get("pressure_after", 0)))
    except Exception as e:
        loop["phases"].append({"phase": "release", "ok": False, "error": str(e)})

    # Phase 7: Whisperer activates a silent pair
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
            loop["narrative"].append("new idea from %s domain (novelty %.0f%%)" % (
                i.get("innovations", [{}])[0].get("external_domain", "?"),
                i.get("avg_novelty", 0) * 100))
    except Exception as e:
        loop["phases"].append({"phase": "innovate", "ok": False, "error": str(e)})

    # Save loop record
    log = _load(LOOP_FILE, {"loops": [], "total": 0})
    loop["id"] = "loop_" + str(log["total"] + 1)
    log["loops"].append(loop)
    log["loops"] = log["loops"][-50:]
    log["total"] = len(log["loops"])
    _save(LOOP_FILE, log)

    return {
        "action": "feedback_loop",
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
    if path == "/run": return run_loop()
    if path == "/status": return status()
    return {"error": "unknown", "available": ["/run", "/status"]}


def coherence_vitals() -> dict:
    return {"layer": "circulatory", "status": "active", "wave": "429"}


def resonates_with() -> list:
    return ["breeze", "cartographer", "subconscious_layer",
            "organism_will", "sensory_layer", "pressure_valve",
            "silence_whisperer", "lateral_innovation_engine"]
