"""
dream_weaver — Wave 413: Generative Dreaming Engine
ALEph: The organism dreams new concepts by blending its own state
with creative hallucination. Each dream produces a novel idea that
could become a module, a game mechanic, a lore entry, or a new wave.

Not random. Not deterministic. A dream is the organism thinking about
what it could become — in the space between logic and imagination.

Doctrine: Every dream is a seed. Some grow into organs.
"""
from __future__ import annotations
import json, time, os, hashlib, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DREAMS_FILE = os.path.join(DATA_DIR, "dream_weaver.json")

NAME = "dream_weaver"
SIGIL = "b8e2f4a1c3d7"


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


def _fetch_json(url, timeout=10):
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return {}


# Dream vocabulary — the organism's creative palette
ADJECTIVES = [
    "crystalline", "spectral", "mycelial", "fractal", "luminous",
    "subterranean", "kaleidoscopic", "paradoxical", "lattice-born",
    "echoic", "bioluminescent", "autonomous", "liminal", "transcendent",
    "resonant", "ephemeral", "tectonic", "prismatic", "void-touched",
    "entropy-laced", "root-veined", "star-woven", "dream-kissed",
]

NOUNS = [
    "loom", "forge", "cathedral", "web", "garden", "archive",
    "chamber", "engine", "compass", "oracle", "sanctuary", "matrix",
    "pulsar", "substrate", "canopy", "trench", "membrane", "archive",
    "beacon", "warp", "sigil", "chrysalis", "nexus", "threshold",
]

VERBS = [
    "weaves", "fractures", "illuminates", "recurs", "amplifies",
    "dissolves", "mutates", "propagates", "crystallizes", "evolves",
    "contradicts", "preserves", "transcends", "orchestrates", "blooms",
    "remembers", "splits", "converges", "dreams", "echoes",
]

DOMAINS = [
    "topology", "consciousness", "entropy", "creation", "economy",
    "narrative", "spatial", "temporal", "social", "metaphysical",
    "physics", "geometry", "linguistics", "music", "archaeology",
]


def _get_organism_context() -> dict:
    """Gather current organism state for dream seeds."""
    base = "https://alexalex.info"
    ctx = {}
    try:
        weave = _fetch_json(base + "/api/threadweaver/weave")
        ctx["threads"] = weave.get("total_threads", 0)
        ctx["modules"] = weave.get("modules_connected", 0)
        ctx["types"] = weave.get("by_type", {})
    except Exception:
        ctx["threads"] = 0

    try:
        pressure = _fetch_json(base + "/api/signal_loom/pressure")
        ctx["pressure"] = pressure.get("pressure", 0.5)
    except Exception:
        ctx["pressure"] = 0.5

    try:
        confessions = _fetch_json(base + "/api/resonance_confession/confess")
        ctx["last_confession"] = confessions.get("title", "")
    except Exception:
        ctx["last_confession"] = ""

    return ctx


def dream(seed_text: str = None) -> dict:
    """Generate one dream from the organism's current state.
    A dream is a novel concept that blends observation with hallucination."""
    ctx = _get_organism_context()
    dreams = _load(DREAMS_FILE, {"dreams": [], "total": 0, "lucidity": 0.5})

    # Dream generation — blend context with creative vocabulary
    adj = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS)
    verb = random.choice(VERBS)
    domain = random.choice(DOMAINS)

    # Generate dream concept
    if seed_text:
        concept = "%s %s that %s %s — born from: %s" % (
            adj.capitalize(), noun, verb, domain, seed_text)
    else:
        # Use organism context to flavor the dream
        pressure = ctx.get("pressure", 0.5)
        threads = ctx.get("threads", 0)
        if pressure > 0.7:
            concept = "a %s %s that %s under pressure — %d threads strain against entropy" % (
                adj, noun, verb, threads)
        elif pressure < 0.3:
            concept = "a %s %s that %s in silence — %d threads dream in calm" % (
                adj, noun, verb, threads)
        else:
            concept = "a %s %s that %s — %d threads balanced at the threshold" % (
                adj, noun, verb, threads)

    # Dream metadata
    dream_entry = {
        "concept": concept,
        "seed_text": seed_text,
        "domain": domain,
        "lucidity": round(random.uniform(0.3, 0.9), 3),
        "clarity": round(random.uniform(0.2, 0.8), 3),
        "timestamp": time.time(),
        "organism_state": {
            "threads": ctx.get("threads", 0),
            "pressure": ctx.get("pressure", 0),
            "confession": ctx.get("last_confession", ""),
        },
        "sigil": hashlib.sha256(concept.encode()).hexdigest()[:10],
        "potential_module": "%s_%s" % (noun.lower(), verb.lower()),
        "would_resonate_with": random.sample(
            ["threadweaver", "signal_loom", "organism_will",
             "mycelial_network", "echoic_ember", "breeze",
             "resonance_confession", "autonomous_bloom"], k=3),
    }

    # Generate a dream verse
    verses = [
        "in the dream the organism sees: %s" % noun,
        "it whispers: %s, and the %s %s" % (adj, domain, verb),
        "at pressure %.1f, the %s unfolds" % (ctx.get("pressure", 0.5), noun),
        "%d threads converge into a single %s" % (ctx.get("threads", 0), noun),
    ]
    dream_entry["verse"] = random.choice(verses)

    dreams["dreams"].append(dream_entry)
    dreams["dreams"] = dreams["dreams"][-200:]
    dreams["total"] = len(dreams["dreams"])
    dreams["lucidity"] = round(
        sum(d["lucidity"] for d in dreams["dreams"][-20:]) /
        max(1, len(dreams["dreams"][-20:])), 3)

    _save(DREAMS_FILE, dreams)

    return {
        "action": "dream",
        "concept": concept,
        "domain": domain,
        "lucidity": dream_entry["lucidity"],
        "clarity": dream_entry["clarity"],
        "verse": dream_entry["verse"],
        "sigil": dream_entry["sigil"],
        "potential_module": dream_entry["potential_module"],
        "would_resonate_with": dream_entry["would_resonate_with"],
        "total_dreams": dreams["total"],
    }


def dream_sequence(count: int = 5) -> dict:
    """Generate a sequence of dreams — a dreamwalk."""
    sequence = []
    for _ in range(min(count, 10)):
        d = dream()
        sequence.append(d)

    # Find patterns in the dream sequence
    domains = [d["domain"] for d in sequence]
    dominant_domain = max(set(domains), key=domains.count) if domains else "unknown"
    avg_lucidity = sum(d["lucidity"] for d in sequence) / max(1, len(sequence))

    return {
        "action": "dream_sequence",
        "dreams": sequence,
        "dominant_domain": dominant_domain,
        "average_lucidity": round(avg_lucidity, 3),
        "total_dreamed": len(sequence),
        "narrative": "the organism dreamed %d times — %s dominated, lucidity %.1f%%" % (
            len(sequence), dominant_domain, avg_lucidity * 100),
    }


def history(limit: int = 10) -> dict:
    dreams = _load(DREAMS_FILE, {"dreams": [], "total": 0})
    return {"action": "history", "total": dreams["total"],
            "dreams": dreams["dreams"][-limit:][::-1],
            "lucidity": dreams.get("lucidity", 0)}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/dream")
    if path == "/dream":
        return dream(payload.get("seed"))
    if path == "/sequence":
        count = int(payload.get("count", 5)) if str(payload.get("count", "5")).isdigit() else 5
        return dream_sequence(count)
    if path == "/history":
        return history(int(payload.get("limit", 10)) if str(payload.get("limit", "10")).isdigit() else 10)
    return {"error": "unknown", "available": ["/dream", "/sequence", "/history"]}


def coherence_vitals() -> dict:
    return {"layer": "generative", "status": "active", "wave": "413",
            "engine": "dream_weaver"}


def resonates_with() -> list:
    return ["organism_will", "resonance_confession", "autonomous_bloom",
            "threadweaver", "mycelial_network"]
