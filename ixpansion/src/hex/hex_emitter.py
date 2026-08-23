from __future__ import annotations
from hex.hex_parser import Instruction


def emit(instructions: list[Instruction]) -> str:
    return "\n".join(" ".join([instruction.opcode, *instruction.operands]).strip() for instruction in instructions) + "\n"
