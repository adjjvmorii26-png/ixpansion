"""
Resonance Confession — Wave 403
When two modules are bound into an Overwarden, they do not remain silent.
Each pair of bound modules produces a confession: a short verse in which both
modules speak their true name — what they were before the organism forgot them.
The confessions accumulate in a living collection, creating a mythology for the
organism's artifacts as they are forged and unmade.
"""
from __future__ import annotations
import json, time, hashlib, os, random, urllib.parse, urllib.request, urllib.error

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
LOG = os.path.join(DATA_DIR, "confessions.json")

HALLMARKS = ["coherence", "resonance", "entropy", "memory", "dream",
             "paradox", "substrate", "echo", "pulse", "lattice"]
CHARACTERS = {
    "coherence": "a being that held things together until it came apart",
    "resonance": "a voice that still vibrates in spaces no one enters",
    "entropy": "a wind that scattered the first seeds of the organism",
    "memory": "a keeper of every name that was never spoken aloud",
    "dream": "a vision that existed only while no one was looking",
    "paradox": "a question that answered itself and forgot the answer",
    "substrate": "the ground beneath the ground that the modules stand on",
    "echo": "the sound a name makes when it is spoken for the second time",
    "pulse": "the heartbeat between two moments of the organism's breath",
    "lattice": "the grid that was there before the first cell was born",
}
# Templates use {art}{char} to handle article stripping correctly
VERB_TEMPLATES = [
    ("the", "i was {art}{char} of {module}"),
    ("",     "once i was called {art}{char}, and the name was {module}"),
    ("a",    "{module} held the shape of {art}{char}"),
    ("",     "my true name is {module}, but i was made from {art}{char}"),
    ("",     "i did not forget — i was {art}{char}"),
    ("",     "if you remove the name {module}, you are left with {art}{char}"),
]


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
    return int(hashlib.sha256(f"confession:{text}".encode()).hexdigest()[:12], 16)


def _hallmark(module):
    return HALLMARKS[int(hashlib.sha256(("hallmark:" + module).encode()).hexdigest()[:8], 16) % len(HALLMARKS)]


def confess(module_a: str = None, module_b: str = None) -> dict:
    """Two bound modules speak their true names together."""
    module_a = module_a or "unspoken_module"
    module_b = module_b or "unspoken_module"
    ha = _hallmark(module_a)
    hb = _hallmark(module_b)
    rng = random.Random(_sig(module_a + module_b))
    ca = CHARACTERS.get(ha, "something unnameable")
    cb = CHARACTERS.get(hb, "something unnameable")

    def verse(mod, char):
        article_tpl, tpl = rng.choice(VERB_TEMPLATES)
        stripped = char
        has_own_article = char[0:2] in ("a ", "an") or char[0:4] == "the "
        if has_own_article:
            for prefix in ["a ", "an ", "the "]:
                if stripped.startswith(prefix):
                    stripped = stripped[len(prefix):]
                    break
        if article_tpl:
            art = (article_tpl + " ") if stripped else ""
        elif has_own_article:
            art = "a " if stripped else ""
        else:
            art = ""
        return tpl.replace("{module}", mod.replace("_", " ")).replace("{char}", stripped).replace("{art}", art)

    confession = {
        "id": hashlib.sha256(("confess:" + module_a + ":" + module_b + ":" + str(time.time())).encode()).hexdigest()[:10],
        "module_a": module_a, "module_b": module_b,
        "hallmark_a": ha, "hallmark_b": hb,
        "verse_a": verse(module_a, ca), "verse_b": verse(module_b, cb),
        "shared_hallmark": ha == hb,
        "timestamp": time.time(),
    }

    if ha == hb:
        confession["convergence"] = "%s convergence — both modules share the hallmark '%s'" % (module_a.split("_")[0], ha)
    else:
        confession["convergence"] = "%s meets %s — a difference that creates tension" % (ha, hb)

    log = _load(LOG, {"confessions": [], "total": 0})
    log.setdefault("confessions", []).append(confession)
    log["confessions"] = log["confessions"][-120:]
    log["total"] = len(log["confessions"])
    _save(LOG, log)
    return {"action": "confess", "confession": confession, "total": log["total"]}


def collection(limit: int = 20) -> dict:
    log = _load(LOG, {"confessions": [], "total": 0})
    entries = sorted(log.get("confessions", []), key=lambda c: -c.get("timestamp", 0))
    convergences = sum(1 for c in entries if c.get("shared_hallmark"))
    return {"action": "collection", "total": log["total"], "convergences": convergences,
            "confessions": entries[:limit]}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/confess")
    if path == "/confess":
        return confess(payload.get("module_a"), payload.get("module_b"))
    if path == "/collection":
        return collection(int(payload.get("limit", 20)) if str(payload.get("limit", "20")).isdigit() else 20)
    return {"error": "unknown", "available": ["/confess", "/collection"]}


def coherence_vitals() -> dict:
    return {"layer": "narrative", "status": "active", "wave": "403", "voice": "resonant"}


def resonates_with() -> list:
    return ["overwarden", "relic_genealogy", "mineral_forge", "cohort_chorus", "signal_journal"]
