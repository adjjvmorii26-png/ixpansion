from __future__ import annotations
from typing import Any

from hex.hex_parser import parse


class HexVM:
    def __init__(self, source: str | None = None) -> None:
        self.memory: dict[str, Any] = {}
        self.stack: list[Any] = []
        self.outputs: list[Any] = []
        if source:
            self.execute(source)

    def execute(self, source: str) -> list[Any]:
        self.stack.clear()
        self.outputs.clear()
        for instruction in parse(source):
            opcode, operands = instruction.opcode, instruction.operands
            if opcode == "PUSH":
                value: Any = operands[0]
                try:
                    value = int(value)
                except ValueError:
                    pass
                self.stack.append(value)
            elif opcode in ("STORE", "LOAD"):
                if not operands or operands[0] not in self.memory and opcode == "LOAD":
                    raise KeyError(f"missing memory operand for {opcode}")
                if opcode == "STORE":
                    self.memory[operands[0]] = self.stack.pop()
                else:
                    self.stack.append(self.memory[operands[0]])
            elif opcode in ("ADD", "SUB"):
                right = self.stack.pop()
                left = self.stack.pop()
                self.stack.append(left + right if opcode == "ADD" else left - right)
            elif opcode == "EMIT":
                self.outputs.append(self.stack.pop())
            elif opcode == "HALT":
                break
        return self.outputs
