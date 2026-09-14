"""Tests for Wave 97 — HEX Runtime."""
import pytest
from api.wave97_hex_runtime import (
    HexProgram, HexRuntime, INSTRUCTIONS, coherence_vitals, handler,
)

PROG_MNEMONIC = "PUSH 5\nPUSH 3\nADD\nDREAM 1\nGLYPH 7\nHALT"
PROG_HEX = "1005100320ff"


class TestHexProgram:
    def test_parse_mnemonic(self):
        p = HexProgram(PROG_MNEMONIC)
        assert p.parse() is True
        assert len(p.instructions) == 6

    def test_parse_hex_bytecode(self):
        p = HexProgram(PROG_HEX)
        assert p.parse() is True
        ops = [mn for mn, _ in p.instructions]
        assert ops == ["PUSH", "PUSH", "ADD", "HALT"]

    def test_parse_empty(self):
        p = HexProgram("")
        assert p.parse() is False
        assert p.error == "empty program"

    def test_parse_unknown_instruction(self):
        p = HexProgram("BOGUS 1")
        assert p.parse() is False
        assert "unknown instruction" in p.error

    def test_parse_odd_hex(self):
        p = HexProgram("abc")
        assert p.parse() is False

    def test_parse_truncated_operands(self):
        p = HexProgram("10")  # PUSH with no operand byte
        assert p.parse() is False
        assert "truncated" in p.error

    def test_program_hash(self):
        p1, p2 = HexProgram(PROG_MNEMONIC), HexProgram(PROG_MNEMONIC)
        assert p1.program_hash == p2.program_hash


class TestHexRuntime:
    def test_run_arithmetic(self):
        rt = HexRuntime()
        p = HexProgram("PUSH 5\nPUSH 3\nADD\nHALT")
        p.parse()
        out = rt.run(p)
        assert out["ok"] is True
        assert out["stack"] == [8]

    def test_run_hex_bytecode(self):
        rt = HexRuntime()
        p = HexProgram(PROG_HEX)
        p.parse()
        out = rt.run(p)
        assert out["stack"] == [8]
        assert out["halted"] is True

    def test_run_dream_physics(self):
        rt = HexRuntime(coherence=0.8, mood="chaotic")
        p = HexProgram("PUSH 4\nDREAM 1\nHALT")
        p.parse()
        out = rt.run(p)
        assert out["ok"] is True
        assert out["stack"] != [4]  # dream transforms the value

    def test_run_branch(self):
        rt = HexRuntime()
        p = HexProgram("PUSH 0\nJMPZ 5\nGLYPH 1\nHALT\nGLYPH 9\nHALT")
        p.parse()
        out = rt.run(p)
        assert out["glyphs"] == ["\U0001f701glyph_9"]

    def test_step_budget(self):
        rt = HexRuntime()
        p = HexProgram("\n".join(["NOP"] * 2000) + "\nHALT")
        p.parse()
        out = rt.run(p)
        assert out["ok"] is False
        assert "budget" in out["error"]

    def test_step_single(self):
        rt = HexRuntime()
        p = HexProgram("PUSH 1\nHALT")
        p.parse()
        out = rt.step(p)
        assert out["ok"] is True
        assert out["trace"]["op"] == "PUSH"

    def test_vitals(self):
        rt = HexRuntime()
        vitals = rt.coherence_vitals()
        assert vitals["wave"] == 97
        assert vitals["instruction_count"] == len(INSTRUCTIONS)


class TestHandler:
    def test_status(self):
        out = handler({"action": "status"})
        assert out["action"] == "status"
        assert out["wave"] == 97
        assert len(out["instructions"]) == len(INSTRUCTIONS)

    def test_run(self):
        out = handler({"action": "run", "source": PROG_MNEMONIC, "mood": "chaotic"})
        assert out["result"]["ok"] is True
        assert out["result"]["stack"] != []

    def test_run_bad_source(self):
        out = handler({"action": "run", "source": "BOGUS"})
        assert out["ok"] is False

    def test_history(self):
        out = handler({"action": "history"})
        assert out["action"] == "history"

    def test_reset(self):
        out = handler({"action": "reset"})
        assert out["message"] == "Runtime reset"

    def test_unknown_action(self):
        out = handler({"action": "bogus"})
        assert out["ok"] is False

    def test_coherence_vitals(self):
        vitals = coherence_vitals()
        assert vitals["wave"] == 97
