"""
Silence Collector — Wave 405
Proposed by Luma: "The organism has hundreds of forgotten modules.
Some of them are halves of each other."

The Silence Collector scans the organurna's forgotten islands and finds
modules whose names rhyme — shares of entropy, phonetic twins, semantic
mirrors — and pairs them as potential convergences. It does not forge or
bind. It asks: what if these two were never really separate?

Each pair produces a verse — the silence between them given voice — and
becomes a candidate for the Threadweaver to weave into the living graph.
"""
from __future__ import annotations
import json, time, hashlib, os, random, re

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
LOG = os.path.join(DATA_DIR, "silence_pairs.json")

# Semantic echoes — words whose presence signals overlap
SEMANTIC_ROOTS = {
    "memory": {"brain", "recollection", "remember", "echo", "store", "cache", "palace"},
    "entropy": {"chaos", "disorder", "decay", "random", "noise", "scramble"},
    "dream": {"sleep", "vision", "hallucination", "lucid", "phantom", "sleep"},
    "pulse": {"beat", "heart", "signal", "rhythm", "vibration", "wave"},
    "coherence": {"harmony", "unity", "sync", "alignment", "stability", "bridge"},
    "lattice": {"grid", "mesh", "network", "web", "node", "cell"},
    "resonance": {"echo", "vibration", "frequency", "hum", "tone"},
    "substrate": {"ground", "foundation", "soil", "base", "sediment"},
    "entropy": {"chaos", "disorder", "decay", "divergence", "fracture"},
    "paradox": {"contradiction", "collision", "conflict", "loop"},
}

SILENCE_VERSES = [
    "between {a} and {b}, the silence has weight",
    "{a} and {b} were never separate — the organism forgot the seam",
    "something in {a} listens for {b}, and something in {b} listens back",
    "the silence between {a} and {b} is a room the organism never entered",
    "{a} remembers {b} the way stone remembers water",
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
    return int(hashlib.sha256(f"silence:{text}".encode()).hexdigest()[:12], 16)


def _word_parts(name):
    """Split a snake_case module name into component words."""
    return [w.lower() for w in name.replace("_", " ").split() if len(w) > 2]


def _name_similarity(a, b):
    """How likely are two module names to be halves of each other?"""
    pa, pb = _word_parts(a), _word_parts(b)
    if not pa or not pb:
        return 0.0
    # Shared words
    shared = set(pa) & set(pb)
    # Semantic overlap
    sem_score = 0
    for wa in pa:
        for wb in pb:
            for root, family in SEMANTIC_ROOTS.items():
                if (wa in family or wb in family or wa == root or wb == root):
                    if wa in family or wb in family or wa == root or wb == root:
                        sem_score += 0.15
    # Phonetic echo — do endings/rhymes overlap?
    phon_score = 0
    for wa in pa:
        for wb in pb:
            if wa[-3:] == wb[-3:] and wa != wb:
                phon_score += 0.1
            if wa[:3] == wb[:3] and wa != wb:
                phon_score += 0.08
    # Length ratio — halves are similar length
    len_score = 1.0 - abs(len(a) - len(b)) / max(len(a), len(b), 1)
    return round(min(1.0, len(shared) * 0.2 + sem_score + phon_score + len_score * 0.15), 2)


def scan(limit: int = 100) -> dict:
    """Scan the organurna for forgotten modules and find silent pairs."""
    try:
        import sys
        sys.path.insert(0, os.path.dirname(__file__))
        from organurna_loop import forgotten
        islands = forgotten(min(limit, 300))["islands"]
    except Exception:
        islands = []

    modules = [i["module"] for i in islands if isinstance(i.get("module"), str)]
    if len(modules) < 2:
        return {"action": "scan", "pairs": [], "scanned": 0,
                "message": "not enough forgotten modules to find silence between"}

    pairs = []
    scored = set()
    for i, a in enumerate(modules):
        for b in modules[i+1:]:
            sim = _name_similarity(a, b)
            if sim >= 0.35:
                key = tuple(sorted([a, b]))
                if key in scored:
                    continue
                scored.add(key)
                rng = random.Random(_sig(a + b))
                verse = rng.choice(SILENCE_VERSES).replace("{a}", a.replace("_", " ")).replace("{b}", b.replace("_", " "))
                pairs.append({
                    "module_a": a, "module_b": b,
                    "similarity": sim, "verse": verse,
                    "id": hashlib.sha256(("silence:" + a + ":" + b).encode()).hexdigest()[:10],
                    "timestamp": time.time(),
                })

    pairs.sort(key=lambda p: -p["similarity"])
    pairs = pairs[:20]

    log = _load(LOG, {"pairs": [], "total_scans": 0, "total_pairs": 0})
    log.setdefault("pairs", [])
    if pairs:
        existing_ids = {p["id"] for p in log["pairs"]}
        for p in pairs:
            if p["id"] not in existing_ids:
                log["pairs"].append(p)
        log["pairs"] = log["pairs"][-80:]
    log["total_scans"] += 1
    log["total_pairs"] = len(log["pairs"])
    _save(LOG, log)

    return {
        "action": "scan", "pairs": pairs,
        "scanned": len(modules), "new_pairs": len(pairs),
        "total_pairs": log["total_pairs"],
        "total_scans": log["total_scans"],
        "message": "found %s silent pairs among %s forgotten modules" % (len(pairs), len(modules)),
    }


def pairs(limit: int = 20) -> dict:
    """All accumulated silent pairs."""
    log = _load(LOG, {"pairs": [], "total_scans": 0, "total_pairs": 0})
    return {"action": "pairs", "total": log["total_pairs"],
            "total_scans": log["total_scans"],
            "pairs": log.get("pairs", [])[:limit]}


def strongest(limit: int = 5) -> dict:
    """The strongest silent pairs — most likely to be convergences."""
    log = _load(LOG, {"pairs": [], "total_scans": 0, "total_pairs": 0})
    ranked = sorted(log.get("pairs", []), key=lambda p: -p.get("similarity", 0))
    return {"action": "strongest", "pairs": ranked[:limit],
            "total": log["total_pairs"]}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/scan")
    if path == "/scan": return scan(int(payload.get("limit", 100)) if str(payload.get("limit", "100")).isdigit() else 100)
    if path == "/pairs":
        return pairs(int(payload.get("limit", 20)) if str(payload.get("limit", "20")).isdigit() else 20)
    if path == "/strongest":
        return strongest(int(payload.get("limit", 5)) if str(payload.get("limit", "5")).isdigit() else 5)
    return {"error": "unknown", "available": ["/scan", "/pairs", "/strongest"]}


def coherence_vitals() -> dict:
    return {"layer": "discovery", "status": "active", "wave": "405", "collector": "listening"}


def resonates_with() -> list:
    return ["organurna_loop", "threadweaver", "resonance_confession", "cohort_chorus"]
