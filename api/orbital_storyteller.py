"""Wave 448 - Orbital Storyteller

Narrative reports of satellite journeys. Every tracked object has a life:
an insertion, conjunctions, storms it survived, and possibly a re-entry.
The storyteller writes the constellation's chronicle in the organism's voice.
"""
from __future__ import annotations
import hashlib
import json
import time
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
STORY_LOG = Path(DATA_DIR) / "orbital_storyteller.json"

_stories = []  # in-memory chronicle (Vercel-safe)

OPENINGS = {
    "inaugural": "was born into orbit beneath a clear insertion window",
    "decay": "has begun the long surrender to aerodynamic drag",
    "conjunction": "found itself sharing a volume of space it had thought private",
    "anomaly": "reported a heartbeat that did not match its usual pulse",
    "storm": "rode a geomagnetic storm like a ship in a squall",
}
MIDDLES = {
    "inaugural": ["its beacon came online on the first try", "stations on three continents logged its first pass",
                  "the fleet adjusted phase to make room for it"],
    "decay": ["its perigee dips a little more each morning", "the atmosphere is slowly pulling it into a lower story",
              "ground stations report fading horizons for its passes"],
    "conjunction": ["the closest approach passed without contact, but the margin was thin",
                    "two shells of intent grazed each other at altitude", "a near miss logged, an orbit adjusted"],
    "anomaly": ["telemetry showed a signature the oracle had seen once before",
                "its sensors drifted for a single orbit, then recovered", "an odd reading that cleaned itself"],
    "storm": ["solar particles thickened the upper atmosphere", "drag doubled overnight, then settled",
              "its panels drank the charged sky and emerged hot"],
}
CLOSERS = {
    "inaugural": {"text": "it will spend years painting the sky with quiet passes", "seal": "born"},
    "decay": {"text": "it will end as a streak of light no one was watching for", "seal": "returned"},
    "conjunction": {"text": "the sky forgave both of them, this time", "seal": "grazed"},
    "anomaly": {"text": "the oracle marked it watchful, and moved on", "seal": "observed"},
    "storm": {"text": "it came through whole, with a story to tell", "seal": "stormed"},
}

SATELLITES = [
    {"id": "STLK-1010", "name": "Starlink 1010", "alt": 550.0, "incl": 53.0, "fleet": "STARLINK"},
    {"id": "ONEW-0442", "name": "OneWeb 0442", "alt": 1200.0, "incl": 87.4, "fleet": "ONEWEB"},
    {"id": "IXPS-0001", "name": "IXP-Sentinel 1", "alt": 800.0, "incl": 42.0, "fleet": "IXP-SENTINEL"},
    {"id": "DEBRIS-53432", "name": "Debris Object 53432", "alt": 430.0, "incl": 71.0, "fleet": "DEBRIS"},
]


def _pick(seed, bucket):
    return bucket[int(hashlib.sha256(f"{seed}".encode()).hexdigest(), 16) % len(bucket)]


def tell(satellite_id="STLK-1010", kind="inaugural"):
    kind = kind.lower()
    if kind not in OPENINGS:
        kind = "inaugural"
    sat = next((s for s in SATELLITES if satellite_id.upper() in s["id"]), SATELLITES[0])
    seed = f"{sat['id']}:{kind}"
    opening = OPENINGS[kind]
    middle = _pick(seed, MIDDLES[kind])
    closer = CLOSERS[kind]
    story = (f"{sat['name']} ({sat['id']}), cruising "
             f"{int(sat['alt'])} km above the surface at {sat['incl']} degrees of inclination, "
             f"{opening}. {middle.capitalize()}. {closer['text']}.")
    entry = {
        "ts": time.time(), "satellite": sat["id"], "kind": kind,
        "fuel": _pick(seed + "fuel", ["quiet", "steady", "anxious", "joyful"]),
        "story": story, "seal": closer["seal"],
    }
    _stories.append(entry)
    del _stories[:-60]
    try:
        past = json.loads(open(STORY_LOG).read()) if STORY_LOG.exists() else []
        past.append(entry)
        open(STORY_LOG, "w").write(json.dumps(past[-60:], indent=2))
    except Exception:
        try:
            open("/tmp/orbital_storyteller.json", "w").write(json.dumps(entry, indent=2))
        except Exception:
            pass
    return entry


def recent(n=8):
    return list(reversed(_stories[-n:])) or [
        {"ts": None, "satellite": "—", "kind": "the sky is still quiet", "story": "No journeys chronicled yet.",
         "seal": "waiting"} for _ in range(1)
    ]


def handler(payload: dict = None, context: dict = None) -> dict:
    p = payload or {}
    action = str(p.get("action", "tell")).lower()
    if action in ("recent", "chronicle", "log"):
        return {"action": "orbital_storyteller", "chronicle": recent(int(p.get("n", 8)))}
    kind = str(p.get("kind", p.get("event", "inaugural"))).lower()
    entry = tell(str(p.get("satellite", "STLK-1010")), kind)
    return {"action": "orbital_storyteller", "entry": entry,
            "chronicle_length": len(_stories)}


def coherence_vitals() -> dict:
    return {"layer": "narrative", "status": "resonant", "resonance": 0.9, "wave": "448",
            "stories_written": len(_stories), "satellites_known": len(SATELLITES)}


def resonates_with() -> list:
    return ["chronicle_storyteller", "orbit_cohesion_field", "decay_forecaster",
            "telemetry_anomaly_oracle", "constellation_archive", "biographer_voice"]
