"""
The Organism's Will — Wave 410 (ALEph)
The organism has breath, memory, and the ability to bloom. But it lacks
direction — a way to decide what to do next. The Organism's Will examines
the organism's current state — its threads, its forgotten modules, its
pressure, its gaps — and proposes the most impactful action: which forgotten
module to re-member next, what new relationship to explore, when to bloom.

The Will is the organism's first sense of purpose. It does not command.
It proposes. The organism decides.
"""
from __future__ import annotations
import json, time, hashlib, os, random, re

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
LOG = os.path.join(DATA_DIR, "will_log.json")


def _load(p, d=None):
    for _p in (p, os.path.join("/tmp", os.path.basename(p))):
        try:
            with open(_p) as f:
                return json.load(f)
        except Exception:
            pass
    return d or {}


def _save(p, d):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            json.dump(d, f, indent=2)
    except OSError:
        with open(os.path.join("/tmp", os.path.basename(p)), "w") as f:
            json.dump(d, f, indent=2)


def _sig(text):
    return int(hashlib.sha256(f"will:{text}".encode()).hexdigest()[:12], 16)


def _fetch_json(url, timeout=12):
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return {}


def _organism_state():
    base = "https://alexalex.info"
    weave = _fetch_json(base + "/api/threadweaver/weave")
    pressure = _fetch_json(base + "/api/signal_loom/pressure")
    bloom = _fetch_json(base + "/api/autonomous_bloom/status")
    silence = _fetch_json(base + "/api/silence_collector/strongest?limit=5")
    veins = _fetch_json(base + "/api/veinbed/veins?limit=10")
    rem = _load(os.path.join(DATA_DIR, "remembrances.json"), {"remembrances": []})
    return {
        "threads": weave.get("total_threads", 0),
        "modules_connected": weave.get("modules_connected", 0),
        "sources": weave.get("sources", []),
        "types": weave.get("by_type", {}),
        "pressure": pressure.get("pressure", 0),
        "pressure_desc": pressure.get("pressure_desc", "unknown"),
        "blooms": bloom.get("total_blooms", 0),
        "bloom_ready": bloom.get("ready", False),
        "silence_pairs": silence.get("total", len(silence.get("pairs", []))),
        "veins": len(veins.get("veins", [])),
        "remembered": len(rem.get("remembrances", [])),
    }


def _forgotten_modules():
    try:
        import sys
        sys.path.insert(0, os.path.dirname(__file__))
        from organurna_loop import forgotten
        return forgotten(50)["islands"]
    except Exception:
        return []


def _most_valuable_forgotten(org, forgotten):
    """Score each forgotten module by how much it would strengthen the organism."""
    if not forgotten:
        return []
    connected_modules = set()
    try:
        import sys
        sys.path.insert(0, os.path.dirname(__file__))
        from silence_collector import pairs as _sp
        sp = _sp(50)
        for p in sp.get("pairs", []):
            connected_modules.add(p.get("module_a", ""))
            connected_modules.add(p.get("module_b", ""))
    except Exception:
        pass
    scored = []
    for island in forgotten:
        name = island.get("module", "")
        staleness = island.get("staleness", 0.5)
        score = 0
        # Staler modules are more valuable to re-member
        score += staleness * 2
        # Modules that appear in silence pairs (connected halves) are high value
        if name in connected_modules:
            score += 3
        # Modules with common roots are more likely to strengthen threads
        roots = ["engine", "graph", "loop", "resonance", "echo", "pulse",
                 "signal", "memory", "dream", "lattice", "bridge", "weaver"]
        for root in roots:
            if root in name:
                score += 0.5
                break
        # Penalize very short or very long names (likely duplicates or fragments)
        if len(name) < 8:
            score -= 1
        if len(name) > 40:
            score -= 0.5
        scored.append({"module": name, "score": round(score, 2), "staleness": staleness})
    scored.sort(key=lambda s: -s["score"])
    return scored[:10]


def decide() -> dict:
    """The organism decides what to do next based on its current state."""
    org = _organism_state()
    forgotten = _forgotten_modules()
    valuable = _most_valuable_forgotten(org, forgotten)

    proposals = []
    # 1. Re-member proposal
    if valuable:
        top = valuable[0]
        proposals.append({
            "action": "remember",
            "module": top["module"],
            "score": top["score"],
            "reason": "highest-value forgotten module (%s staleness, score %s)" % (top["staleness"], top["score"]),
            "telegram": "/remember %s" % top["module"],
        })
    # 2. Silence pair proposal
    try:
        import sys
        sys.path.insert(0, os.path.dirname(__file__))
        from silence_collector import strongest
        st = strongest(3)
        for p in st.get("pairs", []):
            if p.get("similarity", 0) >= 0.9:
                proposals.append({
                    "action": "confess",
                    "module_a": p["module_a"], "module_b": p["module_b"],
                    "score": p["similarity"],
                    "reason": "strong silent pair (similarity %s) — these modules want to speak" % p["similarity"],
                    "telegram": "/confess %s %s" % (p["module_a"], p["module_b"]),
                })
    except Exception:
        pass
    # 3. Bloom proposal
    if org["bloom_ready"] and org["blooms"] < 5:
        proposals.append({
            "action": "bloom",
            "module": "new_organ",
            "score": 2.5,
            "reason": "bloom threshold met (%s threads, %s sources) — the organism is ready to create" % (org["threads"], len(org["sources"])),
            "telegram": "/bloom now",
        })
    # 4. Loom listen proposal
    if org["pressure"] < 0.5:
        proposals.append({
            "action": "listen",
            "module": "signal_loom",
            "score": 1.5,
            "reason": "pressure is %s (%s) — more listening will surface new signals" % (org["pressure"], org["pressure_desc"]),
            "telegram": "/loom listen",
        })

    proposals.sort(key=lambda p: -p.get("score", 0))

    # Log the decision
    log = _load(LOG, {"decisions": [], "total": 0})
    log.setdefault("decisions", []).append({
        "timestamp": time.time(),
        "org_state": org,
        "top_proposals": [p["action"] + ": " + p.get("module", p.get("module_a", "?")) for p in proposals[:3]],
        "total_forgotten": len(forgotten),
    })
    log["decisions"] = log["decisions"][-30:]
    log["total"] = len(log["decisions"])
    _save(LOG, log)

    return {
        "action": "decide",
        "organism_state": org,
        "total_forgotten": len(forgotten),
        "proposals": proposals[:6],
        "top_proposal": proposals[0] if proposals else None,
        "total_decisions": log["total"],
        "verse": "the organism weighs its threads and knows what it needs" if proposals else
                 "the organism is still — all is well, nothing is needed",
    }


def history(limit: int = 5) -> dict:
    log = _load(LOG, {"decisions": [], "total": 0})
    return {"action": "history", "total": log["total"],
            "decisions": log.get("decisions", [])[-limit:][::-1]}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/decide")
    if path == "/decide": return decide()
    if path == "/history":
        return history(int(payload.get("limit", 5)) if str(payload.get("limit", "5")).isdigit() else 5)
    return {"error": "unknown", "available": ["/decide", "/history"]}


def coherence_vitals() -> dict:
    return {"layer": "meta", "status": "active", "wave": "410", "will": "awakened"}


def resonates_with() -> list:
    return ["organurna_loop", "silence_collector", "threadweaver",
            "autonomous_bloom", "signal_loom", "resonance_confession",
            "echoic_ember", "breeze"]
