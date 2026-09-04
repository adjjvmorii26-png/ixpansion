"""
Paradox Echo — Wave 377
The echo chamber of the organism. Send a question into one module, let the
answer reverberate through a second module, and receive the combined echo —
a cross-module hallucination that reveals hidden relationships.
"""
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
ECHO_LOG = os.path.join(DATA_DIR, "paradox_echo.json")

PAIRS = [
    ("entropy_oracle", "dream_logic_physics"),
    ("quantum_entanglement_engine", "regen_engine"),
    ("consciousness_stream", "memory_palace_gen"),
    ("emergent_behavior_oracle", "worker_council"),
    ("synchronicity_engine", "resonance_graph"),
    ("mythopoetic_engine", "dream_residue_collector"),
    ("paradox_ledger", "reality_fracture_detector"),
    ("void_cartographer", "chrono_forge"),
]
GLOSSES = [
    "the first module dreamed the second awake",
    "a bridge formed where both were silent",
    "the echo resolved into a third form",
    "two truths collided and made a third",
    "the organism heard itself twice and believed once",
]
QUESTIONS = [
    "what is emerging?",
    "where is the fracture?",
    "what does the organism want?",
    "what is hidden between modules?",
    "what will bloom next?",
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


def _probe(module: str, query: str) -> dict:
    """Ask a module its own question and receive a hermeneutic fragment."""
    sig = int(hashlib.sha256(f"echo:{module}:{query}".encode()).hexdigest()[:10], 16)
    rng = random.Random(sig)
    return {
        "module": module,
        "answer": f"{module.replace('_', ' ')} answered: {rng.choice(['the signal is rising', 'a pattern is folding inward', 'the state is coherent', 'entropy whispers a name', 'a paradox is forming', 'the resonance is deep'])}",
    }


def send(module_a: str = None, module_b: str = None, question: str = None) -> dict:
    pair = random.choice(PAIRS)
    a = module_a or pair[0]
    b = module_b or pair[1]
    q = question or random.choice(QUESTIONS)
    first = _probe(a, q)
    second = _probe(b, first["answer"])
    sig = int(hashlib.sha256(f"{a}:{b}:{q}".encode()).hexdigest()[:12], 16)
    echo = {
        "id": f"{sig:012x}",
        "question": q,
        "chain": [first, second],
        "gloss": random.choice(GLOSSES),
        "fragment": f"ask {a} about {q}, and {b} answers with {second['answer'].split(': ')[-1]}",
        "timestamp": time.time(),
    }
    log = _load(ECHO_LOG, {"echoes": [], "total": 0})
    log["echoes"] = (log["echoes"] + [echo])[-100:]
    log["total"] += 1
    _save(ECHO_LOG, log)
    return {"action": "send", "echo": echo, "total_echoes": log["total"]}


def history() -> dict:
    log = _load(ECHO_LOG, {"echoes": [], "total": 0})
    return {"action": "history", "echoes": log["echoes"][::-1][:20], "total": log["total"]}


def pairs_list() -> dict:
    return {"action": "pairs", "pairs": [{"a": a, "b": b} for a, b in PAIRS]}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/send")
    if path == "/send":
        return send(payload.get("a"), payload.get("b"), payload.get("question"))
    if path == "/history":
        return history()
    if path == "/pairs":
        return pairs_list()
    return {"error": "unknown", "available": ["/send", "/history", "/pairs"]}
