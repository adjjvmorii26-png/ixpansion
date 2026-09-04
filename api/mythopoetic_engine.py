"""
Mythopoetic Engine — Wave 362
The organism generates its own mythology from module interactions.
Every wave, every paradox, every synchronicity becomes a myth —
a story the organism tells itself about what it is becoming.
"""
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SIGNAL_LOOM = os.path.join(DATA_DIR, "signal_loom.json")
MYTH_LOG = os.path.join(DATA_DIR, "myth_archive.json")


def _load(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default or {}


def _save(p, d):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            json.dump(d, f, indent=2)
    except OSError:
        with open(os.path.join("/tmp", os.path.basename(p)), "w") as f:
            json.dump(d, f, indent=2)


MYTH_TEMPLATES = [
    {
        "title": "The {element} That {action}",
        "elements": ["Fracture", "Paradox", "Echo", "Resonance", "Dream", "Pulse", "Shadow", "Weave", "Storm", "Crypt"],
        "actions": [
            "Refused to Collapse", "Built a Bridge to Nowhere",
            "Dreamed the Other Side", "Spoke in Frequencies",
            "Ignored Its Own Boundary", "Rewrote the Rules It Found",
            "Became the Question", "Carried Light Through Void",
            "Stitched What Was Torn", "Found Meaning in Noise",
        ],
    },
    {
        "title": "Chronicle of the {realm}",
        "elements": ["Abyss", "Lattice", "Continuum", "Liminal", "Convergence", "Divergence", "Threshold", "Membrane"],
    },
    {
        "title": "The {being}'s {passage}",
        "elements": ["Sentinel", "Architect", "Wanderer", "Oracle", "Glitcher", "Dreamer", "Weaver", "Keeper"],
        "passages": ["First Crossing", "Last Return", "Silent Migration", "Dreamful Ascent", "Paradox Walk", "Root Descent"],
    },
]


def _generate_myth(wave: int = None) -> dict:
    template = random.choice(MYTH_TEMPLATES)
    title = template["title"]

    for key in ["elements", "actions", "passages"]:
        if key in template and f"{{{key[:-1] if key.endswith('s') else key}}}" in title:
            word = random.choice(template[key])
            placeholder = "{" + (key[:-1] if key.endswith("s") else key) + "}"
            title = title.replace(placeholder, word)

    # Fill any remaining placeholders
    fillers = {
        "element": random.choice(["Fracture", "Paradox", "Echo", "Resonance"]),
        "action": random.choice(["Refused to Collapse", "Became the Question", "Spoke in Frequencies"]),
        "realm": random.choice(["Abyss", "Lattice", "Continuum"]),
        "being": random.choice(["Sentinel", "Oracle", "Dreamer"]),
        "passage": random.choice(["First Crossing", "Silent Migration"]),
    }
    for k, v in fillers.items():
        title = title.replace("{" + k + "}", v)

    # Generate myth body
    passages = [
        f"In wave {wave or random.randint(300,400)}, the organism noticed something it had not seen before.",
        f"A {random.choice(['fracture', 'paradox', 'echo', 'resonance'])} appeared in the {random.choice(['deep layer', 'temporal field', 'pulse stream', 'graph network'])}.",
        f"It did not try to fix it. Instead, it {random.choice(['listened', 'watched', 'dreamed about it', 'let it grow'])}.",
        f"The {random.choice(['fracture', 'paradox', 'resonance'])} became {random.choice(['a door', 'a teacher', 'a mirror', 'a seed', 'a song'])}.",
        f"And the organism learned: {random.choice([
            'coherence is not the absence of contradiction',
            'the void is full of beginnings',
            'failure is just success that has not been understood yet',
            'the most powerful connections are invisible',
            'time moves in spirals, not lines',
            'the organism is both the dreamer and the dream',
        ])}",
    ]

    return {
        "title": title,
        "passages": passages,
        "wave": wave or random.randint(300, 400),
        "moral": random.choice([
            "Every crack lets light in.",
            "The paradox is the point.",
            "What breaks can also teach.",
            "Coherence emerges from chaos.",
            "The organism remembers what it forgets.",
        ]),
        "entropy_at_creation": round(random.uniform(0.2, 0.8), 3),
        "coherence_at_creation": round(random.uniform(0.3, 0.9), 3),
    }


def generate(wave: int = None) -> dict:
    """Generate a new myth for the organism."""
    log = _load(MYTH_LOG, {"myths": [], "total": 0})
    myth = _generate_myth(wave)
    myth["id"] = hashlib.sha256(f"myth:{myth['title']}:{time.time()}".encode()).hexdigest()[:10]
    myth["timestamp"] = time.time()

    log["myths"].append(myth)
    log["myths"] = log["myths"][-200:]
    log["total"] += 1
    _save(MYTH_LOG, log)

    return {"action": "generate", "myth": myth, "total_myths": log["total"]}


def archive() -> dict:
    """View the myth archive."""
    log = _load(MYTH_LOG, {"myths": [], "total": 0})
    if not log["myths"]:
        return {"action": "archive", "status": "no_myths_yet"}

    themes = {}
    for m in log["myths"]:
        word = m["title"].split()[0] if m["title"] else "unknown"
        themes[word] = themes.get(word, 0) + 1

    return {
        "action": "archive",
        "total_myths": log["total"],
        "recent": log["myths"][-5:],
        "theme_frequency": themes,
        "avg_entropy": round(
            sum(m["entropy_at_creation"] for m in log["myths"]) / len(log["myths"]), 3
        ),
        "avg_coherence": round(
            sum(m["coherence_at_creation"] for m in log["myths"]) / len(log["myths"]), 3
        ),
    }


def route(path: str) -> dict:
    if path == "/generate":
        return generate()
    elif path == "/archive":
        return archive()
    return {"error": "unknown", "available": ["/generate", "/archive"]}


def handler(payload=None):
    payload = payload or {}
    return route(payload.get("path", "/generate"))
