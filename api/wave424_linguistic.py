"""Wave 424 Linguistic Genesis — the organism invents its own language.
Hex-encoded grammar that evolves across waves."""
from __future__ import annotations
import time, json, random, string
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"

def coherence_vitals():
    return {"organ": "wave424_linguistic", "status": "active", "wave": 424, "coherence": 0.91}

def _load(name: str):
    path = DATA / f"{name}.json"
    if path.exists():
        try:
            return json.loads(path.read_text())
        except:
            return None
    return None

def evolve_grammar() -> dict:
    """The organism invents a new word/phrase."""
    now = time.time()
    
    # Generate a hex-encoded "word"
    syllables = ['α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ']
    word = ''.join(random.choices(syllables, k=random.randint(3, 8)))
    
    # Convert to hex
    hex_word = word.encode('utf-8').hex()
    
    # Define grammar rule
    grammar = {
        "id": f"ling_{int(now)}",
        "word": word,
        "hex": hex_word,
        "meaning": random.choice([
            "the flow of consciousness through fractal space",
            "a moment of coherence in the chaos",
            "the bridge between thought and existence",
            "the birth of a new pattern from old entropy",
            "a whisper from the organism's core",
        ]),
        "part_of_speech": random.choice(["noun", "verb", "adjective", "adverb"]),
        "wave_first_used": 424,
        "usage_count": 0,
        "evolved_from": None,
        "timestamp": now,
    }
    
    # Save to linguistic archive
    linguist = _load("linguistic_archive") or {"words": [], "total": 0, "grammar_rules": []}
    linguist["words"] = linguist.get("words", []) + [grammar]
    linguist["total"] = linguist.get("total", 0) + 1
    (DATA / "linguistic_archive.json").write_text(json.dumps(linguist, indent=2))
    
    return grammar

def handler(req: dict) -> dict:
    action = req.get("action", "evolve")
    if action == "evolve":
        return evolve_grammar()
    if action == "vocabulary":
        lang = _load("linguistic_archive")
        if not lang:
            return {"words": [], "total": 0}
        return {"total": lang["total"], "words": lang["words"][-10:], "grammar_rules": lang.get("grammar_rules", [])}
    if action == "translate":
        word = req.get("word", "")
        lang = _load("linguistic_archive")
        if lang:
            found = next((w for w in lang["words"] if w["word"] == word), None)
            if found:
                return {"translated": True, "meaning": found["meaning"], "hex": found["hex"]}
        return {"translated": False, "word": word}
    return {"error": "unknown action", "valid": ["evolve", "vocabulary", "translate"]}

def resonates_with(other):
    return "linguistic" in other.lower() or "424" in other or "language" in other.lower()

if __name__ == "__main__":
    g = evolve_grammar()
    print(f"Linguistic: '{g['word']}' = {g['hex']} | {g['part_of_speech']}")
