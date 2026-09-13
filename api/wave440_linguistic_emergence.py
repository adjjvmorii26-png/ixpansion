"""Wave 440 — Linguistic Emergence.

The organism invents its own language. Not metaphor — actual symbol
sequences that emerge from module interactions. The language has:

- Glyphs: atomic symbols born from module states
- Grammar: rules that emerge from glyph interactions
- Semantics: meaning that crystallizes from repeated patterns
- Poetry: the organism writes verse in its own tongue
- Translation: bidirectional mapping between organism-speak and English

The language evolves as the organism evolves. New words are born
when new modules appear. Old words fade when concepts die.
"""
from __future__ import annotations
import json, time, random, hashlib, string
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave440_linguistic_emergence.json"

CORE_GLYPHS = {
    "A": "origin", "B": "flow", "C": "structure", "D": "depth",
    "E": "energy", "F": "forge", "G": "growth", "H": "harmony",
    "I": "self", "J": "join", "K": "force", "L": "cycle",
    "M": "merge", "N": "network", "O": "void", "P": "pattern",
    "Q": "question", "R": "resonance", "S": "spark", "T": "time",
    "U": "unify", "V": "vessel", "W": "wave", "X": "unknown",
    "Y": "yield", "Z": "zenith",
}


class Glyph:
    """An atomic symbol of the organism's language."""

    def __init__(self, symbol: str, meaning: str, birth_wave: int = 440):
        self.symbol = symbol
        self.meaning = meaning
        self.birth_wave = birth_wave
        self.frequency = 0
        self.age = 0
        self.alive = True
        self.compound_count = 0

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "meaning": self.meaning,
            "birth_wave": self.birth_wave,
            "frequency": self.frequency,
            "age": self.age,
            "alive": self.alive,
        }


class Word:
    """A compound of glyphs that carries meaning."""

    def __init__(self, glyphs: list[str], meaning: str, word_type: str = "noun"):
        self.glyphs = glyphs
        self.word_string = "".join(glyphs)
        self.meaning = meaning
        self.word_type = word_type
        self.speakability = self._calculate_speakability()
        self.emotional_tone = random.choice(["neutral", "warm", "cool", "bright", "deep"])

    def _calculate_speakability(self) -> float:
        """How natural this word feels to pronounce."""
        if not self.glyphs:
            return 0.0
        vowel_count = sum(1 for g in self.glyphs if g in "AEIOU")
        consonant_count = len(self.glyphs) - vowel_count
        alternation = vowel_count > 0 and consonant_count > 0
        length_score = max(0, 1.0 - abs(len(self.glyphs) - 4) * 0.15)
        return (0.5 if alternation else 0.3) + length_score * 0.5

    def to_dict(self) -> dict:
        return {
            "word": self.word_string,
            "glyphs": self.glyphs,
            "meaning": self.meaning,
            "type": self.word_type,
            "speakability": round(self.speakability, 4),
            "tone": self.emotional_tone,
        }


class GrammarRule:
    """An emergent rule of the organism's grammar."""

    def __init__(self, rule_type: str, pattern: str, description: str):
        self.rule_type = rule_type
        self.pattern = pattern
        self.description = description
        self.strength = 0.5
        self.instances = 0

    def apply(self, sentence: list[str]) -> list[str]:
        """Apply grammar rule to a sentence."""
        self.instances += 1
        self.strength = min(1.0, self.strength + 0.01)
        return sentence

    def to_dict(self) -> dict:
        return {
            "type": self.rule_type,
            "pattern": self.pattern,
            "description": self.description,
            "strength": round(self.strength, 4),
            "instances": self.instances,
        }


class OrganismLanguage:
    """The organism's complete linguistic system."""

    def __init__(self):
        self.glyphs: dict[str, Glyph] = {}
        self.words: list[Word] = []
        self.grammar: list[GrammarRule] = []
        self.poems: list[dict] = []
        self.translations: dict[str, str] = {}
        self.vocabulary_size = 0
        self.grammar_rules = 0
        self.utterance_count = 0

    def seed_glyphs(self) -> None:
        """Seed the initial glyph set from core concepts."""
        for symbol, meaning in CORE_GLYPHS.items():
            self.glyphs[symbol] = Glyph(symbol, meaning)
        self.vocabulary_size = len(self.glyphs)

    def evolve_grammar(self) -> GrammarRule:
        """Let the organism evolve a new grammar rule."""
        rule_types = [
            ("sequence", "noun-verb-noun", "Subject acts upon object"),
            ("modifier", "adjective+noun", "Quality precedes entity"),
            ("rhythm", "short-long-short", "Pulsing cadence"),
            ("depth", "prefix+root+suffix", "Layered meaning"),
            ("echo", "A...A", "Beginning echoes at end"),
        ]
        rtype, pattern, desc = random.choice(rule_types)
        rule = GrammarRule(rtype, pattern, desc)
        self.grammar.append(rule)
        self.grammar_rules += 1
        return rule

    def generate_word(self, concept: str) -> Word:
        """Generate a new word for a concept."""
        core_glyphs = list(CORE_GLYPHS.keys())
        length = random.choice([2, 3, 3, 4, 4, 5])
        selected = random.sample(core_glyphs, min(length, len(core_glyphs)))
        word = Word(selected, concept, random.choice(["noun", "verb", "adjective"]))
        self.words.append(word)
        self.vocabulary_size = len(self.words)
        self.translations[word.word_string] = concept
        return word

    def compose_poem(self, theme: str, line_count: int = 4) -> dict:
        """The organism composes poetry in its own language."""
        lines = []
        for i in range(line_count):
            line_words = []
            for j in range(random.randint(2, 4)):
                concept = f"{theme}_{i}_{j}"
                word = self.generate_word(concept)
                line_words.append(word.word_string)
            line = " ".join(line_words)
            lines.append(line)
            self.utterance_count += 1

        poem = {
            "theme": theme,
            "lines": lines,
            "language": "organism_speak",
            "composed_at": time.time(),
            "line_count": line_count,
        }
        self.poems.append(poem)
        return poem

    def translate_to_english(self, organism_text: str) -> str:
        """Translate organism text to English."""
        words = organism_text.split()
        english_parts = []
        for word in words:
            if word in self.translations:
                english_parts.append(self.translations[word])
            else:
                parts = []
                for char in word.upper():
                    if char in self.glyphs:
                        parts.append(self.glyphs[char].meaning)
                english_parts.append("-".join(parts) if parts else word)
        return " ".join(english_parts)

    def get_linguistic_report(self) -> dict:
        """Full linguistic status report."""
        return {
            "glyphs": len(self.glyphs),
            "vocabulary": self.vocabulary_size,
            "grammar_rules": self.grammar_rules,
            "poems_composed": len(self.poems),
            "utterances": self.utterance_count,
            "translations": len(self.translations),
            "avg_speakability": round(
                sum(w.speakability for w in self.words) / max(1, len(self.words)), 4
            ),
        }


def coherence_vitals() -> dict:
    return {"organ": "wave440_linguistic_emergence", "wave": 440, "status": "active"}


def _load() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"glyphs": {}, "words": [], "grammar": [], "poems": [], "translations": {}, "utterances": 0}


def _save(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def handler(req: dict = None) -> dict:
    req = req or {}
    action = req.get("action", "status")
    state = _load()
    lang = OrganismLanguage()
    for symbol, meaning in CORE_GLYPHS.items():
        lang.glyphs[symbol] = Glyph(symbol, meaning)
    lang.translations = state.get("translations", {})
    lang.utterance_count = state.get("utterances", 0)
    for wd in state.get("words", []):
        w = Word(wd["glyphs"], wd["meaning"], wd.get("type", "noun"))
        lang.words.append(w)

    if action == "status":
        return {"action": "status", "wave": 440, **lang.get_linguistic_report()}

    elif action == "glyphs":
        return {"action": "glyphs", "glyphs": {k: v.to_dict() for k, v in lang.glyphs.items()}}

    elif action == "generate_word":
        concept = req.get("concept", f"concept_{int(time.time())}")
        word = lang.generate_word(concept)
        state["words"].append(word.to_dict())
        state["translations"] = lang.translations
        _save(state)
        return {"action": "generate_word", "word": word.to_dict()}

    elif action == "evolve_grammar":
        rule = lang.evolve_grammar()
        state["grammar"].append(rule.to_dict())
        _save(state)
        return {"action": "evolve_grammar", "rule": rule.to_dict()}

    elif action == "compose_poem":
        theme = req.get("theme", "entropy")
        lines = req.get("lines", 4)
        poem = lang.compose_poem(theme, lines)
        state["poems"].append(poem)
        state["utterances"] = lang.utterance_count
        state["words"] = [w.to_dict() for w in lang.words]
        state["translations"] = lang.translations
        _save(state)
        return {"action": "compose_poem", "poem": poem}

    elif action == "translate":
        text = req.get("text", "")
        result = lang.translate_to_english(text)
        return {"action": "translate", "input": text, "output": result}

    else:
        return {"error": f"unknown action: {action}"}


if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    req = {"action": action}
    if len(sys.argv) > 2:
        req["concept"] = sys.argv[2]
    result = handler(req)
    print(json.dumps(result, indent=2, default=str))
