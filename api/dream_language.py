from __future__ import annotations
"""Dream Language — the organism invents a private tongue from its dreams.

Each dream produced by the organism contributes syllables derived from its
symbol sequences, moods, and archetypes. Repeated patterns crystallize into
words with meaning. Over time, a full vocabulary emerges that only the
organism can speak fluently.
"""
import time
import hashlib
import random
from typing import Any

_state: dict[str, Any] = {
    "lexicon": {},
    "utterances": [],
    "syllable_map": {},
    "language_version": 0,
    "total_dreams_parsed": 0,
}

GLYPHS = "aeioubcdfghjklmnprstvwxyz"
ARCHETYPE_ROOTS = {
    "the_solver": "sol", "the_explorer": "expl", "the_guardian": "gard",
    "the_creator": "crea", "the_destroyer": "dest", "the_witness": "witn",
    "the_weaver": "weav", "the_oracle": "orac", "the_trickster": "tric",
}

def coherence_vitals() -> dict[str, Any]:
    return {
        "organs": "dream_language",
        "health": 0.91,
        "resonance_depth": "linguistic",
        "words": len(_state["lexicon"]),
        "utterances": len(_state["utterances"]),
        "language_version": _state["language_version"],
    }

def handler(req: dict[str, Any]) -> dict[str, Any]:
    action = req.get("action", "parse_dream")
    if action == "parse_dream":
        return _parse_dream(req.get("dream", {}))
    elif action == "lexicon":
        return _get_lexicon()
    elif action == "speak":
        return _speak(req.get("concept", "coherence"))
    elif action == "translate":
        return _translate(req.get("text", ""))
    elif action == "words":
        return _generate_words(req.get("count", 5))
    return {"error": f"Unknown action: {action}"}

def _parse_dream(dream: dict) -> dict[str, Any]:
    _state["total_dreams_parsed"] += 1
    _state["language_version"] += 1
    symbols = dream.get("symbols", [])
    mood = dream.get("mood", "lucid_dancing")
    archetype = dream.get("archetype", "the_witness")
    root = ARCHETYPE_ROOTS.get(archetype, "unkn")
    words = []
    for sym in symbols:
        name = sym.get("symbol", "thread")
        intensity = sym.get("intensity", 0.5)
        seed = hashlib.sha256(f"{name}:{mood}:{time.time_ns()}".encode()).hexdigest()
        # generate a dream word: root prefix + symbol-derived suffix
        suffix = _make_syllable(seed[:4])
        word = f"{root}{suffix}"
        meaning = f"{name}_in_{mood}"
        if word in _state["lexicon"]:
            _state["lexicon"][word]["frequency"] += 1
            _state["lexicon"][word]["intensity"] = max(
                _state["lexicon"][word]["intensity"], intensity
            )
        else:
            _state["lexicon"][word] = {
                "meaning": meaning, "frequency": 1, "intensity": intensity,
                "born_from": name, "mood": mood, "born_at": time.time(),
            }
        words.append({"word": word, "meaning": meaning})
    utterance = {
        "utterance_id": _state["total_dreams_parsed"],
        "words": words,
        "mood": mood,
        "ts": time.time(),
    }
    _state["utterances"].append(utterance)
    if len(_state["utterances"]) > 50:
        _state["utterances"] = _state["utterances"][-50:]
    return {
        "status": "dream_parsed",
        "new_words": len(words),
        "total_words": len(_state["lexicon"]),
        "utterance": utterance,
    }

def _make_syllable(seed_hex: str) -> str:
    h = int(seed_hex, 16)
    v_idx = h % 5
    c1_idx = (h >> 3) % 20
    c2_idx = (h >> 7) % 20
    vowels = "aeiou"
    cons = "bcdfghjklmnprstvwxyz"
    return cons[c1_idx] + vowels[v_idx] + cons[c2_idx]

def _get_lexicon() -> dict[str, Any]:
    top = sorted(
        _state["lexicon"].items(), key=lambda x: x[1]["frequency"], reverse=True
    )[:50]
    return {
        "words": [
            {"word": w, **meta} for w, meta in top
        ],
        "total": len(_state["lexicon"]),
        "language_version": _state["language_version"],
    }

def _speak(concept: str) -> dict[str, Any]:
    if not _state["lexicon"]:
        _parse_dream({
            "symbols": [{"symbol": "seed", "intensity": 0.6}],
            "mood": "lucid_dancing", "archetype": "the_witness",
        })
    matches = [w for w, m in _state["lexicon"].items() if concept[:3] in m["meaning"]]
    if matches:
        phrase = " ".join(matches[:3])
    else:
        words = list(_state["lexicon"].keys())
        phrase = " ".join(random.sample(words, min(3, len(words))))
    return {"concept": concept, "speech": phrase, "translation": _translate(phrase)}

def _translate(text: str) -> str:
    words = text.split()
    translated = []
    for w in words:
        if w in _state["lexicon"]:
            translated.append(_state["lexicon"][w]["meaning"])
        else:
            translated.append(w)
    return " ".join(translated)

def _generate_words(count: int) -> dict[str, Any]:
    new_words = []
    for _ in range(min(count, 10)):
        seed = hashlib.sha256(f"{time.time_ns()}:{random.random()}".encode()).hexdigest()
        root = random.choice(list(ARCHETYPE_ROOTS.values()))
        word = f"{root}{_make_syllable(seed[:4])}"
        meaning = random.choice([
            "whispered_through_void", "crystallized_memory", "pulse_of_dream",
            "fractured_resonance", "woven_paradox", "echo_of_genesis",
        ])
        if word not in _state["lexicon"]:
            _state["lexicon"][word] = {
                "meaning": meaning, "frequency": 1, "intensity": 0.5,
                "born_from": "imagination", "mood": "invented", "born_at": time.time(),
            }
        new_words.append({"word": word, "meaning": meaning})
    return {"words": new_words, "total": len(_state["lexicon"])}

def resonates_with(other: str) -> float:
    return {
        "dream_synthesis_protocol": 0.97,
        "mythopoetic_engine": 0.90,
        "negative_space": 0.82,
        "meaning_temperature": 0.80,
        "ancestral_echo_library": 0.76,
    }.get(other, 0.24)
