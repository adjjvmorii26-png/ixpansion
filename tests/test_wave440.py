"""Tests for Wave 440 — Linguistic Emergence."""
import pytest
from api.wave440_linguistic_emergence import (
    Glyph, Word, GrammarRule, OrganismLanguage, handler, coherence_vitals, CORE_GLYPHS
)

def test_coherence_vitals():
    v = coherence_vitals()
    assert v["organ"] == "wave440_linguistic_emergence"
    assert v["wave"] == 440

def test_glyph_init():
    g = Glyph("A", "origin")
    assert g.symbol == "A"
    assert g.meaning == "origin"
    assert g.alive is True

def test_word_init():
    w = Word(["A", "B", "C"], "flowing origin")
    assert w.word_string == "ABC"
    assert 0 <= w.speakability <= 1

def test_word_speakability():
    w = Word(["A", "E", "I"], "vowels")
    assert w.speakability > 0
    w2 = Word(["B", "C", "D", "F", "G"], "consonants")
    assert w2.speakability >= 0

def test_grammar_rule():
    r = GrammarRule("sequence", "noun-verb-noun", "Subject acts upon object")
    result = r.apply(["a", "b", "c"])
    assert len(result) == 3
    assert r.instances == 1

def test_language_init():
    lang = OrganismLanguage()
    assert lang.vocabulary_size == 0

def test_language_seed_glyphs():
    lang = OrganismLanguage()
    lang.seed_glyphs()
    assert len(lang.glyphs) == 26

def test_language_generate_word():
    lang = OrganismLanguage()
    lang.seed_glyphs()
    word = lang.generate_word("test_concept")
    assert word.meaning == "test_concept"
    assert len(lang.words) == 1

def test_language_compose_poem():
    lang = OrganismLanguage()
    lang.seed_glyphs()
    poem = lang.compose_poem("entropy", 3)
    assert poem["theme"] == "entropy"
    assert len(poem["lines"]) == 3
    assert lang.utterance_count == 3

def test_language_translate():
    lang = OrganismLanguage()
    lang.seed_glyphs()
    lang.generate_word("test")
    result = lang.translate_to_english("A")
    assert "origin" in result

def test_handler_status():
    result = handler({"action": "status"})
    assert result["action"] == "status"
    assert result["wave"] == 440

def test_handler_glyphs():
    result = handler({"action": "glyphs"})
    assert result["action"] == "glyphs"
    assert len(result["glyphs"]) == 26

def test_handler_generate_word():
    result = handler({"action": "generate_word", "concept": "test"})
    assert result["action"] == "generate_word"
    assert result["word"]["meaning"] == "test"

def test_handler_evolve_grammar():
    result = handler({"action": "evolve_grammar"})
    assert result["action"] == "evolve_grammar"
    assert "rule" in result

def test_handler_compose_poem():
    result = handler({"action": "compose_poem", "theme": "dream", "lines": 3})
    assert result["action"] == "compose_poem"
    assert len(result["poem"]["lines"]) == 3

def test_handler_translate():
    result = handler({"action": "translate", "text": "A"})
    assert result["action"] == "translate"
    assert "origin" in result["output"]

def test_handler_unknown():
    result = handler({"action": "unknown"})
    assert "error" in result

def test_core_glyphs_complete():
    assert len(CORE_GLYPHS) == 26

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
