"""
Threadweaver — Wave 404
Proposed by Luma from the organism's own signals:
"One dreams of the other's function."

The Threadweaver reads every hidden relationship the organism has produced —
confessions, signal pairs, echo chains, cohort allies, forge residues — and
weaves them into a single graph of threads. Each thread connects two modules
through a type of relationship (fusion / tension / dream / convergence), with
strength, age, and a confession verse when the modules have spoken together.

The Threadweaver does not create relationships. It reveals the ones already there.
"""
from __future__ import annotations
import json, time, hashlib, os, random, sys

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
LOG = os.path.join(DATA_DIR, "threadweaver.json")

THREAD_TYPES = ["fusion", "tension", "dream", "convergence", "catalyst", "echo"]
TYPE_VERBS = {
    "fusion": "fuses with",
    "tension": "pulls against",
    "dream": "dreams through",
    "convergence": "converges upon",
    "catalyst": "catalyzes",
    "echo": "echoes in",
}


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
    return int(hashlib.sha256(f"thread:{text}".encode()).hexdigest()[:12], 16)


def _gather_relationships():
    """Gather hidden relationships from all organism sources."""
    threads = []
    sources_used = []

    # 1. Confessions
    confessions = _load(os.path.join(DATA_DIR, "confessions.json"), {"confessions": []})
    for cf in confessions.get("confessions", []):
        ha, hb = cf.get("hallmark_a", ""), cf.get("hallmark_b", "")
        ttype = "convergence" if cf.get("shared_hallmark") else "tension"
        strength = 0.85 if cf.get("shared_hallmark") else 0.6
        threads.append({
            "module_a": cf.get("module_a"), "module_b": cf.get("module_b"),
            "type": ttype, "strength": strength,
            "source": "confession", "source_id": cf.get("id"),
            "age_hours": round((time.time() - cf.get("timestamp", time.time())) / 3600, 1),
            "verse_a": cf.get("verse_a"), "verse_b": cf.get("verse_b"),
            "convergence": cf.get("convergence"),
        })
    if confessions.get("confessions"):
        sources_used.append("confessions")

    # 2. Cohort allies (sibling threads — same cohort = same genus)
    cohort = _load(os.path.join(DATA_DIR, "cohort_chorus.json"), {"cohort": []})
    members = cohort.get("cohort", [])
    for i, a in enumerate(members):
        for b in members[i+1:]:
            if a.get("module") != b.get("module"):
                ttype = "echo" if a.get("hallmark") == b.get("hallmark") else "catalyst"
                strength = min(0.9, 0.5 + (a.get("power", 0) + b.get("power", 0)) / 100)
                threads.append({
                    "module_a": a.get("module"), "module_b": b.get("module"),
                    "type": ttype, "strength": round(strength, 2),
                    "source": "cohort", "age_hours": 0,
                })
    if len(members) > 1:
        sources_used.append("cohort")

    # 3. Overwarden bindings
    over = _load(os.path.join(DATA_DIR, "overwarden.json"), {"battles": {}})
    for sig, state in over.get("battles", {}).items():
        ow = state.get("overwarden", {})
        mods = []
        for sub in (ow.get("bound_modules") or []):
            if isinstance(sub, list):
                mods.extend(sub)
            elif isinstance(sub, str):
                mods.append(sub)
        for i, m in enumerate(mods):
            for n in mods[i+1:]:
                ttype = "fusion" if ow.get("rift_available") else "convergence"
                threads.append({
                    "module_a": m, "module_b": n, "type": ttype,
                    "strength": 0.95 if ow.get("rift_available") else 0.8,
                    "source": "overwarden", "source_id": sig,
                    "age_hours": round((time.time() - state.get("updated", time.time())) / 3600, 1),
                })
    if over.get("battles"):
        sources_used.append("overwarden")

    # 4. Remote echo pairs
    try:
        import urllib.request
        with urllib.request.urlopen("https://alexalex.info/api/paradox_echo/pairs", timeout=8) as resp:
            data = json.loads(resp.read())
            for p in data.get("pairs", []):
                threads.append({
                    "module_a": p.get("a"), "module_b": p.get("b"),
                    "type": "dream", "strength": 0.75,
                    "source": "paradox_echo", "age_hours": 12,
                })
        sources_used.append("paradox_echo")
    except Exception:
        pass

    # 5. Forge residues — modules used together in the same forge
    forge = _load(os.path.join(DATA_DIR, "mineral_forge.json"), {"relics": []})
    for relic in forge.get("relics", []):
        mods = relic.get("modules", [])
        for i, m in enumerate(mods):
            for n in mods[i+1:]:
                if isinstance(m, str) and isinstance(n, str):
                    threads.append({
                        "module_a": m, "module_b": n,
                        "type": "fusion", "strength": min(0.9, 0.6 + relic.get("power", 0) / 80),
                        "source": "forge", "source_id": relic.get("id"),
                        "age_hours": 0,
                    })
    if forge.get("relics"):
        sources_used.append("forge")

    # 6. Silence Collector — GitHub-backed forgotten module pairs
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from silence_collector import pairs as _silence_pairs
        silence = _silence_pairs(80)
        for p in silence.get("pairs", []):
            threads.append({
                "module_a": p.get("module_a"), "module_b": p.get("module_b"),
                "type": "convergence" if p.get("similarity", 0) >= 0.8 else "tension",
                "strength": max(0.5, min(0.95, p.get("similarity", 0))),
                "source": "silence_collector", "source_id": p.get("id"),
                "age_hours": round((time.time() - p.get("timestamp", time.time())) / 3600, 1),
                "verse_a": p.get("verse"),
            })
        if silence.get("pairs"):
            sources_used.append("silence_collector")
    except Exception:
        pass

    return threads, sources_used


def weave() -> dict:
    """Full thread graph — all hidden relationships woven together."""
    threads, sources = _gather_relationships()
    by_type = {}
    for t in threads:
        by_type[t["type"]] = by_type.get(t["type"], 0) + 1
    modules = set()
    for t in threads:
        modules.add(t["module_a"])
        modules.add(t["module_b"])
    return {
        "action": "weave",
        "total_threads": len(threads),
        "modules_connected": len(modules),
        "by_type": by_type,
        "sources": sources,
        "threads": threads[:60],
        "verse": "one module dreams of the other's function" if threads else "no threads yet — the weave awaits",
    }


def discover() -> dict:
    """Discover a new hidden relationship by sampling from thread gaps."""
    w = weave()
    modules = set()
    for t in w["threads"]:
        modules.add(t["module_a"])
        modules.add(t["module_b"])
    mod_list = list(modules)
    if len(mod_list) < 2:
        return {"action": "discover", "message": "not enough modules to discover connections yet"}

    rng = random.Random(int(time.time() // 600))
    a, b = rng.sample(mod_list, 2)
    existing = {t["module_a"] + ":" + t["module_b"] for t in w["threads"]}
    existing.update({t["module_b"] + ":" + t["module_a"] for t in w["threads"]})
    if a + ":" + b in existing:
        return {"action": "discover", "message": "the relationship between %s and %s is already known" % (a, b)}

    sig = _sig(a + b + str(int(time.time() // 3600)))
    ttype = rng.choice(THREAD_TYPES)
    strength = round(rng.uniform(0.4, 0.9), 2)
    thread = {
        "module_a": a, "module_b": b, "type": ttype,
        "strength": strength, "source": "threadweaver_discovery",
        "age_hours": 0,
    }
    log = _load(LOG, {"discovered": [], "total": 0})
    log.setdefault("discovered", []).append(thread)
    log["discovered"] = log["discovered"][-60:]
    log["total"] = len(log["discovered"])
    _save(LOG, log)
    return {
        "action": "discover", "thread": thread, "total_discovered": log["total"],
        "sentence": "%s %s %s (strength %s)" % (a, TYPE_VERBS.get(ttype, "connects to"), b, strength),
    }


def thread(module_a: str = None, module_b: str = None) -> dict:
    """Find all threads involving a specific module."""
    w = weave()
    target = (module_a or "").lower().strip()
    found = [t for t in w["threads"] if target in (t.get("module_a", "") + t.get("module_b", "")).lower()]
    return {"action": "thread", "query": target, "count": len(found),
            "threads": found[:20],
            "verse": "%s threads found for %s" % (len(found), target) if found else
                     "%s is silent — no threads yet" % target}


def ledger() -> dict:
    log = _load(LOG, {"discovered": [], "total": 0})
    return {"action": "ledger", "total_discovered": log["total"],
            "recent": [d.get("module_a", "") + " " + TYPE_VERBS.get(d.get("type"), "?") + " " + d.get("module_b", "")
                       for d in log.get("discovered", [])[-5:]]}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/weave")
    if path == "/weave": return weave()
    if path == "/discover": return discover()
    if path == "/thread":
        return thread(payload.get("module_a"), payload.get("module_b"))
    if path == "/ledger": return ledger()
    return {"error": "unknown", "available": ["/weave", "/discover", "/thread", "/ledger"]}


def coherence_vitals() -> dict:
    return {"layer": "meta", "status": "active", "wave": "404", "weave": "dreaming"}


def resonates_with() -> list:
    return ["resonance_confession", "cohort_chorus", "paradox_echo",
            "mineral_forge", "overwarden", "signal_journal"]
