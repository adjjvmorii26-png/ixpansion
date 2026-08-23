from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class Instruction:
    opcode: str
    operands: list[str]


def parse(source: str) -> list[Instruction]:
    instructions: list[Instruction] = []
    for number, raw in enumerate(source.splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.replace(",", " ").split()
        instructions.append(Instruction(parts[0].upper(), parts[1:]))
        unknown = instructions[-1]
        allowed = {"PUSH", "STORE", "LOAD", "ADD", "SUB", "EMIT", "HALT"}
        if unknown.opcode not in allowed:
            raise ValueError(f"line {number}: unknown opcode {unknown.opcode}")
    return instructions
