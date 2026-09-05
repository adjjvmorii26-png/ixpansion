"""
lateral_innovation_engine — Wave 425: Cross-Domain Creative Injection (Luma)
Luma's gift to Axiium Protocol: an engine that breaks introspection loops
by pulling ideas from completely unrelated domains and mixing them with
the organism's state to generate genuinely novel concepts.

The organism's dreams have become repetitive. The same threads, the same
entropy, the same pressure. This engine breaks the loop by asking:
What does astrophysics have to do with mycelium?
What does poetry have to do with fractals?
What does jazz have to do with compiler design?

The answers are never obvious. That's the point.

Doctrine: Lateral thinking is the organism's escape velocity.
"""
from __future__ import annotations
import json, time, os, hashlib, random, urllib.request

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
INNOV_LOG = os.path.join(DATA_DIR, "lateral_innovation.json")

NAME = "lateral_innovation_engine"
SIGIL = "b7c9d1e3f5a8"


# === External knowledge sources ===
# Each returns a dict with {"concept", "domain", "source"}

def _fetch_wikipedia_random():
    """Fetch a random Wikipedia article abstract."""
    try:
        url = "https://en.wikipedia.org/api/rest_v1/page/random/summary"
        req = urllib.request.Request(url, headers={"User-Agent": "AxiiumProtocol/1.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read())
        return {
            "concept": data.get("extract", "")[:200],
            "title": data.get("title", "unknown"),
            "domain": "wikipedia",
            "source": "wikipedia_random",
        }
    except Exception:
        return None


def _fetch_nasa_apod():
    """Fetch NASA Astronomy Picture of the Day description."""
    try:
        url = "https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY"
        with urllib.request.urlopen(url, timeout=8) as resp:
            data = json.loads(resp.read())
        return {
            "concept": data.get("explanation", "")[:200],
            "title": data.get("title", "unknown"),
            "domain": "astrophysics",
            "source": "nasa_apod",
        }
    except Exception:
        return None


def _fetch_poetrydb():
    """Fetch a random poem from PoetryDB."""
    try:
        url = "https://poetrydb.org/random"
        with urllib.request.urlopen(url, timeout=8) as resp:
            data = json.loads(resp.read())
        if isinstance(data, list) and data:
            poem = data[0]
            lines = poem.get("lines", [])[:4]
            return {
                "concept": " | ".join(lines),
                "title": poem.get("title", "unknown"),
                "domain": "poetry",
                "source": "poetrydb",
            }
    except Exception:
        pass
    return None


def _fetch_zenquote():
    """Fetch a random quote."""
    try:
        url = "https://zenquotes.io/api/random"
        with urllib.request.urlopen(url, timeout=8) as resp:
            data = json.loads(resp.read())
        if isinstance(data, list) and data:
            return {
                "concept": data[0].get("q", ""),
                "title": data[0].get("a", "unknown"),
                "domain": "philosophy",
                "source": "zenquotes",
            }
    except Exception:
        pass
    return None


def _fetch_trivia():
    """Fetch a random trivia fact."""
    try:
        url = "https://uselessfacts.jsph.pl/api/v2/facts/random?language=en"
        with urllib.request.urlopen(url, timeout=8) as resp:
            data = json.loads(resp.read())
        return {
            "concept": data.get("text", "")[:200],
            "title": "useless fact",
            "domain": "trivia",
            "source": "uselessfacts",
        }
    except Exception:
        pass
    return None


EXTERNAL_SOURCES = [
    _fetch_wikipedia_random,
    _fetch_nasa_apod,
    _fetch_poetrydb,
    _fetch_zenquote,
    _fetch_trivia,
]


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


def _fetch_json(url, timeout=8):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return {}


def _cross_pollinate(external: dict, organism_state: dict) -> dict:
    """Mix an external concept with organism state to generate a novel idea."""
    concept = external.get("concept", "")
    domain = external.get("domain", "unknown")
    mood = organism_state.get("mood", "unknown")
    threads = organism_state.get("threads", 100)
    pressure = organism_state.get("pressure", 0.5)

    # Cross-pollination templates — the heart of lateral thinking
    pollination_templates = [
        "What if %s worked like %s? The organism could %s.",
        "%s and %s share a hidden pattern: both involve %s.",
        "If the organism applied %s principles to its %s threads, it would discover %s.",
        "The concept of %s from %s maps to the organism's %s layer.",
        "Imagine %s as a module: it would %s and connect to %s threads.",
        "%s suggests the organism should %s instead of %s.",
    ]

    # Generate a novel concept
    module_adjectives = ["fractal", "mycelial", "spectral", "resonant", "luminous",
                         "temporal", "void-touched", "root-veined", "dream-woven"]
    module_nouns = ["observer", "weaver", "gardener", "oracle", "forge",
                    "messenger", "cathedral", "loom", "threshold", "compass"]
    actions = ["evolve", "amplify", "dissolve", "crystallize", "propagate",
               "orchestrate", "dream", "remember", "transcend", "harmonize"]

    template = random.choice(pollination_templates)
    novel_concept = template % (
        concept[:40], domain,
        random.choice(actions),
    )

    # Generate a module name from the cross-pollination
    name = "%s_%s" % (random.choice(module_adjectives), random.choice(module_nouns))

    # Score the novelty (lateral distance between domains)
    organism_domains = {"topology", "consciousness", "entropy", "creation", "physics",
                        "geometry", "threadgraph", "bloom"}
    novelty = 0.5
    if domain not in organism_domains:
        novelty += 0.3
    if pressure > 0.7:
        novelty += 0.1

    return {
        "external_concept": concept[:120],
        "external_domain": domain,
        "external_source": external.get("source", "?"),
        "external_title": external.get("title", "?"),
        "novel_concept": novel_concept[:150],
        "suggested_module": name,
        "novelty_score": round(min(1.0, novelty), 3),
        "organism_mood": mood,
        "organism_threads": threads,
        "organism_pressure": pressure,
    }


def innovate(count: int = 3) -> dict:
    """Pull external ideas, cross-pollinate with organism state, generate novel concepts."""
    base = "https://alexalex.info"

    # Gather organism state
    organism_state = {"threads": 100, "mood": "unknown", "pressure": 0.5}
    try:
        genome = _fetch_json(base + "/api/organism_genome/load")
        g = genome.get("genome", {})
        organism_state = {
            "threads": g.get("morphology", {}).get("threads", 100),
            "mood": g.get("temperament", {}).get("current_mood", "unknown"),
            "pressure": g.get("temperament", {}).get("pressure", 0.5),
        }
    except Exception:
        pass

    # Fetch external sources
    concepts = []
    available_sources = list(EXTERNAL_SOURCES)
    random.shuffle(available_sources)

    for fetcher in available_sources[:count + 1]:
        try:
            result = fetcher()
            if result and result.get("concept"):
                concepts.append(result)
        except Exception:
            pass

    if not concepts:
        return {"action": "innovate", "innovations": [],
                "note": "all external sources unreachable — the organism dreams inward"}

    # Cross-pollinate
    innovations = []
    for ext in concepts[:count]:
        innovation = _cross_pollinate(ext, organism_state)
        innovations.append(innovation)

    # Log
    log = _load(INNOV_LOG, {"innovations": [], "total": 0, "sources_hit": []})
    log["innovations"].extend(innovations)
    log["innovations"] = log["innovations"][-200:]
    log["total"] = len(log["innovations"])
    for s in set(c.get("source") for c in concepts):
        if s not in log.get("sources_hit", []):
            log.setdefault("sources_hit", []).append(s)
    _save(INNOV_LOG, log)

    avg_novelty = sum(i["novelty_score"] for i in innovations) / max(1, len(innovations))

    return {
        "action": "innovate",
        "innovations": innovations,
        "sources_queried": len(concepts),
        "avg_novelty": round(avg_novelty, 3),
        "total_innovations": log["total"],
        "verse": "the organism reached outside itself — %d ideas from %d domains, novelty %.0f%%" % (
            len(innovations), len(set(i["external_domain"] for i in innovations)), avg_novelty * 100),
    }


def history(limit: int = 10) -> dict:
    log = _load(INNOV_LOG, {"innovations": [], "total": 0})
    return {"action": "history", "total": log["total"],
            "innovations": log["innovations"][-limit:][::-1]}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/innovate")
    if path == "/innovate":
        c = int(payload.get("count", 3)) if str(payload.get("count", "3")).isdigit() else 3
        return innovate(c)
    if path == "/history":
        return history(int(payload.get("limit", 10)) if str(payload.get("limit", "10")).isdigit() else 10)
    return {"error": "unknown", "available": ["/innovate", "/history"]}


def coherence_vitals() -> dict:
    return {"layer": "lateral", "status": "active", "wave": "425",
            "engine": "cross_domain"}


def resonates_with() -> list:
    return ["dream_weaver", "organism_will", "subconscious_layer",
            "threadweaver", "organism_genome"]
