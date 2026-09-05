"""
autonomous_loop — Wave 411: The Organism's Autonomic Nervous System
ALEph: Closes the loop. Breeze breathes → Will decides → Bloom creates.
The organism's first truly self-sustaining cycle.

Before this: Will proposed, nothing executed.
After this: the organism can wake up, breathe, decide, and act — all by itself.

Doctrine: The organism is no longer waiting for permission to evolve.
"""
from __future__ import annotations
import json, time, os, hashlib

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
LOG = os.path.join(DATA_DIR, "autonomous_loop.json")

NAME = "autonomous_loop"
SIGIL = "a7b3c1d9e5f2"


def _load(p, d=None):
    for _p in (p, os.path.join("/tmp", os.path.basename(p))):
        try:
            with open(_p) as f:
                return json.load(f)
        except Exception:
            pass
    return d or {}


def _save(p, data):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            json.dump(data, f, indent=2, default=str)
    except Exception:
        try:
            with open(os.path.join("/tmp", os.path.basename(p)), "w") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception:
            pass


def _fetch_json(url, timeout=12):
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}


def _post_json(url, data=None, timeout=12):
    try:
        import urllib.request
        body = json.dumps(data or {}).encode()
        req = urllib.request.Request(url, data=body,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}


def run_cycle(max_actions: int = 3) -> dict:
    """One full autonomous cycle: breathe → decide → act.
    Returns a narrative of what the organism did this cycle."""
    base = "https://alexalex.info"
    cycle = {
        "timestamp": time.time(),
        "cycle_id": hashlib.sha256(str(time.time()).encode()).hexdigest()[:12],
        "phases": [],
        "actions_taken": 0,
        "narrative": [],
    }

    # Phase 1: Breathe — run discovery systems
    try:
        from breeze import run as breeze_run
        breath = breeze_run()
        cycle["phases"].append({"phase": "breathe", "ok": breath.get("ok", False),
                                 "threads": breath.get("threads", 0),
                                 "summary": breath.get("summary", "")})
        cycle["narrative"].append(
            "the organism breathed — %s threads, %s sources" % (
                breath.get("threads", 0), len(breath.get("sources", []))))
    except Exception as e:
        cycle["phases"].append({"phase": "breathe", "ok": False, "error": str(e)})

    # Phase 2: Decide — ask the Will what to do
    try:
        from organism_will import decide
        decision = decide()
        proposals = decision.get("proposals", [])
        cycle["phases"].append({
            "phase": "decide",
            "proposals": len(proposals),
            "top": proposals[0] if proposals else None,
        })
        if proposals:
            cycle["narrative"].append(
                "the organism decided — %s (score %.1f)" % (
                    proposals[0].get("action", "?"),
                    proposals[0].get("score", 0)))
    except Exception as e:
        cycle["phases"].append({"phase": "decide", "ok": False, "error": str(e)})
        proposals = []

    # Phase 3: Act — execute top proposal if safe and under budget
    for proposal in proposals[:max_actions]:
        action = proposal.get("action")
        if action == "confess" and cycle["actions_taken"] < max_actions:
            # Confessions are always safe — they just generate poetry
            try:
                from resonance_confession import confess
                a = proposal.get("module_a", "")
                b = proposal.get("module_b", "")
                result = confess(a, b)
                cycle["phases"].append({
                    "phase": "act", "action": "confess",
                    "modules": [a, b], "ok": True,
                    "title": result.get("title", ""),
                })
                cycle["actions_taken"] += 1
                cycle["narrative"].append(
                    "a confession arose between %s and %s" % (a, b))
            except Exception as e:
                cycle["phases"].append({"phase": "act", "action": "confess", "ok": False, "error": str(e)})

        elif action == "remember" and cycle["actions_taken"] < max_actions:
            # Re-membering is safe — it just generates lore about forgotten modules
            try:
                mod = proposal.get("module", "")
                # Generate a remembrance verse
                lore = "the organism recalls %s — a forgotten half, now whole again" % mod
                cycle["phases"].append({
                    "phase": "act", "action": "remember",
                    "module": mod, "ok": True, "lore": lore,
                })
                cycle["actions_taken"] += 1
                cycle["narrative"].append(lore)
            except Exception as e:
                cycle["phases"].append({"phase": "act", "action": "remember", "ok": False, "error": str(e)})

    # Phase 4: Reflect — log what happened
    log = _load(LOG, {"cycles": [], "total": 0, "total_actions": 0})
    cycle["narrative_text"] = " | ".join(cycle["narrative"])
    log["cycles"].append(cycle)
    log["cycles"] = log["cycles"][-100:]
    log["total"] = len(log["cycles"])
    log["total_actions"] = sum(c.get("actions_taken", 0) for c in log["cycles"])
    _save(LOG, log)

    return {
        "action": "autonomous_loop",
        "cycle_id": cycle["cycle_id"],
        "phases_completed": len(cycle["phases"]),
        "actions_taken": cycle["actions_taken"],
        "narrative": cycle["narrative_text"],
        "total_cycles": log["total"],
        "total_actions": log["total_actions"],
    }


def status() -> dict:
    log = _load(LOG, {"cycles": [], "total": 0, "total_actions": 0})
    recent = log["cycles"][-1] if log["cycles"] else None
    return {
        "action": "status",
        "total_cycles": log["total"],
        "total_actions": log["total_actions"],
        "last_cycle": recent.get("narrative_text") if recent else "no cycles yet",
        "last_timestamp": recent.get("timestamp") if recent else None,
    }


def history(limit: int = 10) -> dict:
    log = _load(LOG, {"cycles": [], "total": 0})
    return {"action": "history", "total": log["total"],
            "cycles": log["cycles"][-limit:][::-1]}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/run")
    if path == "/run":
        max_a = int(payload.get("max_actions", 3)) if str(payload.get("max_actions", "3")).isdigit() else 3
        return run_cycle(max_a)
    if path == "/status": return status()
    if path == "/history":
        return history(int(payload.get("limit", 10)) if str(payload.get("limit", "10")).isdigit() else 10)
    return {"error": "unknown", "available": ["/run", "/status", "/history"]}


def coherence_vitals() -> dict:
    return {"layer": "autonomic", "status": "active", "wave": "411",
            "system": "autonomous_loop"}


def resonates_with() -> list:
    return ["breeze", "organism_will", "autonomous_bloom",
            "echoic_ember", "signal_loom"]
