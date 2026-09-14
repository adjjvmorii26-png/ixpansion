"""Tests for Wave 96 — HEX Grammar Evolution."""
import pytest
from api.wave96_hex_grammar_evolution import (
    GrammarRule, HexGrammar, HexGrammarEngine, coherence_vitals, handler,
)


def _hex_grammar() -> HexGrammar:
    grammar = HexGrammar()

    def handle_hex(ctx):
        return f"HEX-{ctx['input'].hex()}"

    grammar.define_rule(
        pattern="484558",  # "HEX"
        handler=handle_hex,
        description="Match HEX magic bytes",
        consumes=1,
        produces=1,
    )

    def handle_grammar(ctx):
        return f"GRAMMAR-{ctx['input'].hex()[:10]}"

    grammar.define_rule(
        pattern="4752414d4d4152",  # "GRAMMAR"
        handler=handle_grammar,
        description="Match GRAMMAR magic bytes",
        consumes=1,
        produces=1,
    )
    return grammar


class TestGrammarRule:
    def test_rule_match(self):
        rule = GrammarRule("R1", "484558", lambda ctx: "ok", "HEX", 1, 1)
        assert rule.match(bytes.fromhex("484558")) is True
        assert rule.match(bytes.fromhex("deadbeef")) is False

    def test_rule_apply(self):
        rule = GrammarRule("R2", "484558", lambda ctx: "ok", "HEX", 1, 1)
        result = rule.apply({"input": bytes.fromhex("484558")})
        assert result == "ok"
        assert rule.times_applied == 1
        assert rule.success_count == 1

    def test_rule_apply_failure_safe(self):
        def boom(ctx):
            raise RuntimeError("nope")

        rule = GrammarRule("R3", "484558", boom, "bad", 1, 1)
        assert rule.apply({"input": bytes.fromhex("484558")}) is None
        assert rule.times_applied == 1


class TestHexGrammar:
    def test_parse_matches(self):
        grammar = _hex_grammar()
        results = grammar.parse(bytes.fromhex("484558"))
        assert len(results) == 1
        rule_id, result = results[0]
        assert result == "HEX-484558"

    def test_parse_no_match(self):
        grammar = _hex_grammar()
        results = grammar.parse(bytes.fromhex("deadbeef"))
        assert results == []

    def test_execute_hex_valid(self):
        grammar = _hex_grammar()
        out = grammar.execute_hex("484558")
        assert out["ok"] is True
        assert out["parsed"] is True

    def test_execute_hex_invalid(self):
        grammar = _hex_grammar()
        out = grammar.execute_hex("zzzz")
        assert out["ok"] is False
        assert "error" in out

    def test_compile_to_operations(self):
        grammar = _hex_grammar()
        ops = grammar.compile_hex_to_operations("484558")
        assert len(ops) == 1
        assert ops[0]["rule_id"] in grammar.rules


class TestHexGrammarEngine:
    def test_interpret(self):
        grammar = _hex_grammar()
        engine = HexGrammarEngine(grammar)
        ops = engine.interpret("484558")
        assert len(ops) == 1

    def test_mutate(self):
        grammar = HexGrammar()
        engine = HexGrammarEngine(grammar)
        engine.mutate(1.0)  # force mutation
        assert len(grammar.rules) >= 1

    def test_status(self):
        grammar = _hex_grammar()
        engine = HexGrammarEngine(grammar)
        status = engine.get_grammar_status()
        assert status["wave"] == 96
        assert status["total_rules"] == 2


class TestHandler:
    def test_status(self):
        out = handler({"action": "status"})
        assert out["action"] == "status"
        assert "grammar_status" in out

    def test_compile(self):
        out = handler({"action": "compile", "hex": "484558"})
        assert out["action"] == "compile"

    def test_evolve(self):
        out = handler({"action": "evolve", "mutation_rate": 1.0})
        assert out["action"] == "evolve"

    def test_unknown_action(self):
        out = handler({"action": "bogus"})
        assert out["ok"] is False

    def test_coherence_vitals(self):
        vitals = coherence_vitals()
        assert vitals["wave"] == 96
        assert "total_rules" in vitals
        assert "language_complexity" in vitals
