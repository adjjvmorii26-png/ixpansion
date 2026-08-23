import pytest

from engine.compilers.hex_to_bytecode import compile_hex
from engine.compilers.bytecode_to_actions import bytecode_to_actions
from hex.hex_emitter import emit
from hex.hex_parser import parse
from hex.vm import HexVM


def test_parse_ignores_comments_and_uppercases_opcodes():
    instructions = parse("push 2 # literal\nemit\nhalt")
    assert [item.opcode for item in instructions] == ["PUSH", "EMIT", "HALT"]


def test_vm_executes_arithmetic_memory_and_output():
    source = "PUSH 2\nSTORE x\nLOAD x\nPUSH 3\nADD\nEMIT\nHALT\nPUSH 99\n"
    vm = HexVM(source)
    assert vm.outputs == [5]
    assert vm.memory["x"] == 2


def test_parser_rejects_unknown_opcode():
    with pytest.raises(ValueError, match="unknown opcode"):
        parse("SELF_DESTRUCT")


def test_emit_round_trips_instructions():
    instructions = parse("push 1\nadd\nhalt")
    assert parse(emit(instructions)) == instructions


def test_engine_compiler_maps_bytecode_to_actions():
    bytecode = compile_hex("PUSH 1\nSTORE x\nEMIT\nHALT")
    actions = bytecode_to_actions(bytecode)
    assert {"type": "store", "target": "x"} in actions
    assert {"type": "emit"} in actions
