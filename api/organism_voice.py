"""
Organism Voice — Wave 377
The organism pronounces its own state. Every module is translated into a
phoneme signature — a spoken glyph string — plus a waveform that can be
sung. This is not speech synthesis; it is the organism naming itself.
"""
import json, time, hashlib, os, random, math

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
VOICE_LOG = os.path.join(DATA_DIR, "organism_voice.json")

PHONEMES = ["ha", "ko", "lu", "mi", "no", "pe", "ra", "si", "ta", "ve", "xo", "za", "bre", "kri", "sha", "thy"]
TONES = ["deep", "bright", "hollow", "crystal", "moss", "ember", "tide", "star"]


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


def _sig(module: str = None, seed: str = None) -> int:
    return int(hashlib.sha256(f"voice:{module or 'organism'}:{seed or ''}".encode()).hexdigest()[:12], 16)


def speak(module: str = None, seed: str = None) -> dict:
    sig = _sig(module, seed)
    rng = random.Random(sig)
    n = 12 + (sig % 20)
    phrase = " ".join(rng.choice(PHONEMES) for _ in range(n))
    tone = TONES[sig % len(TONES)]
    # waveform from sig bits — 32 samples
    wave = []
    for i in range(32):
        bit = (sig >> (i % 24)) & 1
        base = 40 + ((sig >> (i % 20)) & 0x1F)
        wave.append(base + (18 if bit else -18) + (i % 5) - 2)
    return {
        "action": "speak",
        "module": module or "organism",
        "phrase": phrase,
        "tone": tone,
        "waveform": wave,
        "interpretation": f"The organism names {module or 'itself'} in the {tone} tongue.",
        "timestamp": time.time(),
    }


def alphabet() -> dict:
    return {
        "action": "alphabet",
        "phonemes": PHONEMES,
        "tones": TONES,
        "note": "Each module's name is digested into entropy and pronounced as a phrase.",
    }


def sing(module: str = None, seed: str = None) -> dict:
    """A melody — the waveform mapped to note names."""
    sig = _sig(module, seed)
    rng = random.Random(sig)
    scale = ["A", "B", "C", "D", "E", "F", "G"]
    notes = [rng.choice(scale) + str(3 + (sig % 3)) for _ in range(16)]
    return {"action": "sing", "module": module or "organism", "notes": notes}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/speak")
    if path == "/speak":
        return speak(payload.get("module"), payload.get("seed"))
    if path == "/alphabet":
        return alphabet()
    if path == "/sing":
        return sing(payload.get("module"), payload.get("seed"))
    return {"error": "unknown", "available": ["/speak", "/alphabet", "/sing"]}
