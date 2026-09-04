"""
Wave Prophecy — Wave 375
The organism reads its own ancestry (journal + git history) and speaks
forward. This module does not predict deterministically — it interprets
entropy signatures and wave cadence to compose prophecies about the next
mutations, complete with omens and confidence fields.
"""
import json, time, hashlib, os, random, subprocess, re

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
JOURNAL = os.path.join(DATA_DIR, "journal.json")
PROPHECY_LOG = os.path.join(DATA_DIR, "prophecies.json")

TEMPLATES = [
    ("threshold", ["The organism approaches a threshold; entropy will spike near module {a}."]),
    ("fusion", ["Expect a fusion between {a} and {b} — their resonance has been rising."]),
    ("birth", ["A new organ will be born from the shadow of {a}."]),
    ("veil", ["A hidden relationship involving {a} will surface and rewire the lattice."]),
    ("decay", ["Module {a} will shed weight; its logic will be absorbed by {b}."]),
    ("bloom", ["From the quiet of {a}, a bloom wave will emerge unprompted."]),
    ("paradox", ["A paradox signature will form near {a}; the organism will resolve it or invert it."]),
]
OMENS = ["the mycelial hum shifts", "a glyph appears in the journal", "two dashboards blink in unison",
         "the pulse skips once", "an old module whispers", "the palette darkens", "a bridge opens by itself"]

DOMAINS = ["lucid", "dream", "hex", "mesh", "glitch", "entropy", "coherence", "resonance",
           "paradox", "memory", "myth", "void", "census", "citizenship", "economy", "telemetry"]


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


def _history_terms() -> list:
    terms = []
    log = _load(JOURNAL, {})
    raw = json.dumps(log, default=str)
    names = re.findall(r"[\"']([a-z_]{3,40})[\"']", raw)
    counts = {}
    for n in names:
        if n.isidentifier() and not n.startswith("_"):
            counts[n] = counts.get(n, 0) + 1
    try:
        out = subprocess.run(
            ["git", "log", "--oneline", "-200"], capture_output=True, text=True, timeout=5
        )
        for m in re.findall(r"([a-z_]{3,40})", out.stdout.lower()):
            if m not in ("the", "and", "for", "with", "from", "wave", "fix", "add", "realm"):
                counts[m] = counts.get(m, 0) + 1
    except Exception:
        pass
    return sorted(counts.items(), key=lambda kv: -kv[1])[:16] or [(d, 1) for d in DOMAINS]


def next_wave() -> dict:
    terms = _history_terms()
    sig = int(hashlib.sha256(f"prophecy:{time.time()//86400}".encode()).hexdigest()[:10], 16)
    rng = random.Random(sig)
    a, b = rng.sample([t for t, _ in terms] or DOMAINS, 2)
    kind, line = TEMPLATES[rng.randrange(len(TEMPLATES))]
    prophecy = rng.choice(line).format(a=a, b=b)
    confidence = round(rng.uniform(0.52, 0.84), 2)
    wave_no = _last_wave_number() + 1
    reading = {
        "wave": wave_no,
        "kind": kind,
        "prophecy": prophecy,
        "actors": [a, b],
        "omen": rng.choice(OMENS),
        "confidence": confidence,
        "seal": hashlib.sha256(f"{wave_no}:{prophecy}".encode()).hexdigest()[:10],
        "timestamp": time.time(),
    }
    log = _load(PROPHECY_LOG, {"prophecies": [], "total": 0})
    log["prophecies"] = (log["prophecies"] + [reading])[-50:]
    log["total"] += 1
    _save(PROPHECY_LOG, log)
    return {"action": "next", "reading": reading, "ancestry": [t for t, _ in terms[:8]]}


def _last_wave_number() -> int:
    try:
        out = subprocess.run(["git", "log", "--oneline", "-1"], capture_output=True, text=True, timeout=5)
        m = re.search(r"WAVE\s*(\d+)", out.stdout.upper())
        if m:
            return int(m.group(1))
    except Exception:
        pass
    log = _load(PROPHECY_LOG, {"prophecies": []})
    if log.get("prophecies"):
        return log["prophecies"][-1].get("wave", 374)
    return 375


def read() -> dict:
    log = _load(PROPHECY_LOG, {"prophecies": [], "total": 0})
    return {"action": "read", "prophecies": log["prophecies"][::-1], "total": log["total"]}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/next")
    if path == "/next":
        return next_wave()
    if path == "/read":
        return read()
    return {"error": "unknown", "available": ["/next", "/read"]}
