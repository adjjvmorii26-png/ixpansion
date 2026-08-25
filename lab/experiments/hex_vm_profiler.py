#!/usr/bin/env python3
"""Hex VM Profiler — analyze and visualize HEX instruction execution.

Bridges hex_parser + hex_emitter + vm to profile HEX program execution.
Tracks instruction frequency, stack depth over time, memory usage,
and identifies hot loops. Creates a "execution fingerprint" that
characterizes the program's behavior pattern.
"""
from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class InstructionTrace:
    line: int
    opcode: str
    stack_before: int
    stack_after: int
    memory_keys: int
    output_count: int


@dataclass
class HexProgram:
    source: str
    instructions: list[dict[str, Any]]

    @classmethod
    def from_source(cls, source: str) -> "HexProgram":
        instructions = []
        for i, line in enumerate(source.strip().splitlines(), 1):
            stripped = line.split("#")[0].strip()
            if not stripped:
                continue
            parts = stripped.replace(",", " ").split()
            opcode = parts[0].upper()
            operands = parts[1:]
            instructions.append({
                "line": i,
                "opcode": opcode,
                "operands": operands,
            })
        return cls(source=source, instructions=instructions)


@dataclass
class HexVMProfiler:
    """Profile HEX program execution without running it."""
    max_stack: int = 100
    max_memory: int = 256

    def profile(self, program: HexProgram) -> dict[str, Any]:
        traces: list[InstructionTrace] = []
        stack_depth = 0
        memory_keys: set[str] = set()
        output_count = 0
        opcode_freq: dict[str, int] = Counter()
        stack_timeline: list[int] = []
        max_stack_seen = 0
        loop_candidates: list[dict[str, Any]] = []

        for instr in program.instructions:
            opcode = instr["opcode"]
            operands = instr["operands"]
            stack_before = stack_depth
            opcode_freq[opcode] += 1

            if opcode == "PUSH":
                stack_depth += 1
            elif opcode in ("ADD", "SUB"):
                stack_depth = max(0, stack_depth - 1)
            elif opcode == "STORE":
                if operands:
                    memory_keys.add(operands[0])
                    stack_depth = max(0, stack_depth - 1)
            elif opcode == "LOAD":
                stack_depth += 1
            elif opcode == "EMIT":
                stack_depth = max(0, stack_depth - 1)
                output_count += 1
            elif opcode == "HALT":
                pass

            max_stack_seen = max(max_stack_seen, stack_depth)
            stack_timeline.append(stack_depth)

            traces.append(InstructionTrace(
                line=instr["line"],
                opcode=opcode,
                stack_before=stack_before,
                stack_after=stack_depth,
                memory_keys=len(memory_keys),
                output_count=output_count,
            ))

            # Detect potential loops (repeated opcode patterns)
            if len(traces) >= 3:
                last_3 = [t.opcode for t in traces[-3:]]
                if last_3[0] == last_3[1] == last_3[2] and opcode not in ("HALT",):
                    loop_candidates.append({
                        "line": instr["line"],
                        "pattern": last_3[0],
                        "depth": stack_depth,
                    })

        # Stack variance
        if stack_timeline:
            mean_stack = sum(stack_timeline) / len(stack_timeline)
            variance = sum((s - mean_stack) ** 2 for s in stack_timeline) / len(stack_timeline)
            stack_stability = max(0.0, 1.0 - math.sqrt(variance) / max(1, max_stack_seen))
        else:
            stack_stability = 0.0

        # Execution fingerprint
        fp_data = {
            "total_instructions": len(program.instructions),
            "unique_opcodes": len(opcode_freq),
            "max_stack": max_stack_seen,
            "outputs": output_count,
            "memory_cells": len(memory_keys),
        }
        fingerprint = hashlib.sha256(
            json.dumps(fp_data, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()[:16]

        return {
            "summary": {
                "total_instructions": len(program.instructions),
                "opcode_distribution": dict(opcode_freq.most_common()),
                "max_stack_depth": max_stack_seen,
                "final_stack_depth": stack_depth,
                "memory_cells_used": len(memory_keys),
                "outputs": output_count,
                "stack_stability": round(stack_stability, 4),
                "halts_cleanly": any(i["opcode"] == "HALT" for i in program.instructions),
            },
            "loop_candidates": loop_candidates[:5],
            "fingerprint": fingerprint,
            "traces": [
                {
                    "line": t.line,
                    "opcode": t.opcode,
                    "stack": t.stack_after,
                }
                for t in traces
            ],
        }


def demo() -> dict[str, Any]:
    profiler = HexVMProfiler()

    programs = {
        "counter": """PUSH 0
STORE counter
LOAD counter
PUSH 1
ADD
STORE counter
LOAD counter
EMIT
HALT""",
        "fibonacci": """PUSH 0
STORE a
PUSH 1
STORE b
LOAD a
LOAD b
ADD
STORE c
LOAD c
EMIT
HALT""",
        "swap_and_emit": """PUSH 10
PUSH 20
STORE temp
EMIT
LOAD temp
EMIT
HALT""",
    }

    results = {}
    for name, source in programs.items():
        program = HexProgram.from_source(source)
        results[name] = profiler.profile(program)

    return results


def main() -> None:
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
