from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class Instruction:
    opcode: str
    operands: list[str]
    line_number: int = 0


OPERAND_ARITY = {
    "PUSH": (1, 1),
    "STORE": (1, 1),
    "LOAD": (1, 1),
    "ADD": (0, 0),
    "SUB": (0, 0),
    "EMIT": (0, 0),
    "HALT": (0, 0),
}


def parse(source: str) -> list[Instruction]:
    instructions: list[Instruction] = []
    for number, raw in enumerate(source.splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.replace(",", " ").split()
        opcode = parts[0].upper()
        if opcode not in OPERAND_ARITY:
            raise ValueError(f"line {number}: unknown opcode {opcode}")
        minimum, maximum = OPERAND_ARITY[opcode]
        count = len(parts) - 1
        if not minimum <= count <= maximum:
            raise ValueError(f"line {number}: {opcode} expects {minimum} operand(s)")
        instructions.append(Instruction(opcode, parts[1:], number))
    return instructions
