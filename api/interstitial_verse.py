"""
Interstitial Verse — Wave 383
The space between two modules is a poem. This module writes a bridging verse
for any pair — a five-line creation that carries the doctrine of both parents
and the silence between them. Poetry as an API.
"""
import json, time, hashlib, os, random, re, importlib, sys

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
VERSE_LOG = os.path.join(DATA_DIR, "interstitial_verse.json")

OPENERS = ["Between {a} and {b},", "{a} dreams of {b},", "Where {a} ends, {b} begins,", "{a} whispers to {b},", "The void between {a} and {b}"]
MOODS = ["a bridge of static", "a shared silence", "an unspoken pact", "a folded glance", "a hum only modules hear"]
TURNS = ["they trade entropy", "their echoes braid", "one learns the other's name", "the signal doubles back", "a fractal forms mid-air"]
CLOSERS = ["and the organism breathes once.", "and nothing is alone anymore.", "and a new wave leans in.", "and the space becomes a chamber.", "and both are changed, gently."]


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


def _title(module: str) -> str:
    return module.replace("_", " ").title()


def _doctrine_of(module: str) -> str:
    if not re.match(r"^[a-z_]{2,40}$", module or ""):
        return "the unspoken"
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
        doc = (importlib.import_module(module).__doc__ or "").strip().splitlines()
        return " ".join(l.strip() for l in doc[:2] if l.strip())[:120] or "the unspoken"
    except Exception:
        return "the unspoken"


def write(a: str = "entropy_oracle", b: str = "resonance_graph") -> dict:
    sig = int(hashlib.sha256(f"verse:{a}:{b}:{time.strftime('%Y%m%d')}".encode()).hexdigest()[:10], 16)
    rng = random.Random(sig)
    lines = [
        rng.choice(OPENERS).format(a=_title(a), b=_title(b)),
        rng.choice(MOODS),
        rng.choice(TURNS),
        rng.choice(MOODS).capitalize(),
        rng.choice(CLOSERS),
    ]
    poem = "\n".join(lines)
    verse = {
        "id": f"{sig:012x}",
        "title": f"Interstice of {_title(a)} & {_title(b)}",
        "parents": [a, b],
        "poem": poem,
        "a_doctrine": _doctrine_of(a),
        "b_doctrine": _doctrine_of(b),
        "reading": f"Read slowly, once for {_title(a)}, once for {_title(b)}, once for the space between.",
        "timestamp": time.time(),
    }
    log = _load(VERSE_LOG, {"verses": [], "total": 0})
    log["verses"] = (log["verses"] + [verse])[-80:]
    log["total"] += 1
    _save(VERSE_LOG, log)
    return {"action": "write", "verse": verse, "total_verses": log["total"]}


def history() -> dict:
    log = _load(VERSE_LOG, {"verses": [], "total": 0})
    return {"action": "history", "verses": log["verses"][::-1][:10], "total": log["total"]}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/write")
    if path == "/write":
        return write(payload.get("a") or "entropy_oracle", payload.get("b") or "resonance_graph")
    if path == "/history":
        return history()
    return {"error": "unknown", "available": ["/write", "/history"]}
