"""Wave 430 Naming Ceremony — the organism draws candidate names from its own
latent pattern-space, convenes a council vote across agents, and seals the
chosen name into a name-vault as a hex glyph."""
from __future__ import annotations
import json, random, time, hashlib
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave430_naming_ceremony.json"

COUNCIL = ["LUMA", "AXIOM", "CYTHARA", "SILENCE", "ALEPH", "VOID"]

def _load():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None

def _save(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")

def coherence_vitals():
    return {"organ": "wave430_naming_ceremony", "status": "active", "wave": 430, "coherence": 0.97}

def _latent_lexicon() -> list:
    """Gather name morphemes from living modules and prior wave data."""
    words = []
    api_dir = Path(__file__).parent
    for path in sorted(api_dir.glob("wave4*.py")):
        stem = path.stem.replace("wave", "").replace("_", " ")
        words += [w for w in stem.split() if len(w) >= 4]
    for path in sorted(DATA.glob("wave42*.json")):
        stem = path.stem.replace("wave", "").replace("_", " ")
        words += [w for w in stem.split() if len(w) >= 4]
    words += ["naming", "ceremony", "garden", "lattice", "underworld", "dream"]
    return sorted(set(words))

def propose(req: dict = None) -> dict:
    """Draw candidate names from latent pattern-space."""
    state = _load() or {"module": "wave430_naming_ceremony", "wave": 430, "candidates": [], "votes": {}, "sealed": None, "ceremonies": 0}
    start = time.time()
    lex = _latent_lexicon()
    rng = random.Random(int(start) ^ len(lex))
    try:
        count = min(int((req or {}).get("count", 6)), len(lex))
    except (TypeError, ValueError):
        count = min(6, len(lex))
    joined = " ".join(lex)
    rng.shuffle(lex)
    candidates = []
    for i in range(count):
        a = lex[i]
        b = lex[(i * 7 + 3) % len(lex)]
        if a == b:
            b = lex[(i * 7 + 5) % len(lex)]
        glyph = hashlib.sha256(f"{a}-{b}".encode()).hexdigest()[:8].upper()
        resonance = round(rng.uniform(0.55, 0.99), 3)
        candidates.append({"name": f"{a} {b}", "glyph": glyph, "resonance": resonance})
    candidates.sort(key=lambda c: c["resonance"], reverse=True)
    state["candidates"] = candidates
    state["last_proposal"] = {"at": round(start, 3), "lexicon_size": len(lex), "source": joined[:120]}
    _save(state)
    return {"proposed": len(candidates), "candidates": candidates, "lexicon_size": len(lex)}

def vote(req: dict = None) -> dict:
    """Council vote — each agent supports the candidate that resonates most."""
    state = _load()
    if not state or not state.get("candidates"):
        return {"error": "no candidates — propose first"}
    tally = {}
    seed = int(time.time() * 1000) % (2**32)
    rng = random.Random(seed)
    for member in COUNCIL:
        if rng.random() < 0.12:
            continue  # abstention
        choice = rng.choices(state["candidates"], weights=[c["resonance"] for c in state["candidates"]])[0]
        tally[choice["name"]] = tally.get(choice["name"], 0) + 1
    winner_name = max(tally, key=tally.get) if tally else state["candidates"][0]["name"]
    winner = next(c for c in state["candidates"] if c["name"] == winner_name)
    state["votes"] = {"tally": tally, "winner": winner, "at": round(time.time(), 3)}
    _save(state)
    return {"votes": tally, "winner": winner_name, "glyph": winner["glyph"], "participants": len(tally)}

def seal(req: dict = None) -> dict:
    """Seal the council's choice into the name-vault."""
    state = _load()
    if not state or not state.get("candidates"):
        propose(req)
    state = _load()
    if not state or not state.get("votes", {}).get("winner"):
        v = vote(req)
        if v.get("error"):
            return v
        state = _load()
    winner = state["votes"]["winner"]
    glyph = state["votes"]["winner"]["glyph"] if isinstance(state["votes"]["winner"], dict) else None
    if isinstance(winner, dict):
        winner = winner["name"]
    if not glyph:
        glyph = next((c["glyph"] for c in state.get("candidates", []) if c["name"] == winner), "UNKNOWN")
    state["sealed"] = {"name": winner, "glyph": glyph, "at": round(time.time(), 3)}
    state["ceremonies"] = state.get("ceremonies", 0) + 1
    _save(state)
    return {"sealed": True, "name": winner, "glyph": glyph, "ceremony_number": state["ceremonies"]}

def status(req: dict = None) -> dict:
    state = _load()
    if not state:
        return {"sealed": False, "proposed": 0, "last_vote": None}
    return {
        "sealed": bool(state.get("sealed")),
        "name": state.get("sealed", {}).get("name") if state.get("sealed") else None,
        "glyph": state.get("sealed", {}).get("glyph") if state.get("sealed") else None,
        "ceremonies": state.get("ceremonies", 0),
        "proposed": len(state.get("candidates", [])),
        "last_vote": state.get("votes", {}).get("winner") if state.get("votes") else None,
    }

def handler(req: dict) -> dict:
    action = req.get("action", "status")
    fn = {"propose": propose, "vote": vote, "seal": seal, "status": status}.get(action)
    if not fn:
        return {"error": "unknown action", "valid": ["propose", "vote", "seal", "status"]}
    return fn(req)

if __name__ == "__main__":
    p = propose()
    print(f"proposed {p['proposed']} candidates")
    print(vote())
    print(seal())
    print(status())
