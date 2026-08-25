"""HEX Virtual Machine — Stack-based interpreter for HEX scripts and grammars.

Supports opcodes: PUSH, STORE, LOAD, ADD, SUB, EMIT, HALT
Supports grammar directives: TOPOLOGY, CHANNEL, ANOMALY
"""
from __future__ import annotations
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

VALID_OPCODES = {"PUSH", "STORE", "LOAD", "ADD", "SUB", "EMIT", "HALT"}
GRAMMAR_DIRECTIVES = {"TOPOLOGY", "CHANNEL", "ANOMALY", "OPCODE"}


class HexVM:
    """Stack-based virtual machine for HEX programs."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.stack: list[Any] = []
        self.memory: dict[str, Any] = {}
        self.output: list[Any] = []
        self.program_counter = 0
        self.program: list[tuple[str, str]] = []
        self.halted = False
        self.steps = 0
        self.max_steps = 10000

    def parse_line(self, line: str) -> tuple[str, str] | None:
        """Parse a single HEX instruction line."""
        line = line.split("#")[0].strip()  # Remove comments
        if not line:
            return None
        parts = line.split(None, 1)
        opcode = parts[0].upper()
        operand = parts[1] if len(parts) > 1 else ""
        return (opcode, operand)

    def load_script(self, script: str) -> int:
        """Load a HEX script (multi-line string). Returns instruction count."""
        self.program = []
        for line in script.splitlines():
            parsed = self.parse_line(line)
            if parsed:
                # Skip grammar directives — they're metadata, not executable
                if parsed[0] not in GRAMMAR_DIRECTIVES:
                    self.program.append(parsed)
        return len(self.program)

    def load_file(self, path: str | Path) -> int:
        """Load a HEX script from a file."""
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"HEX script not found: {p}")
        return self.load_script(p.read_text())

    def execute(self) -> dict:
        """Execute the loaded program. Returns execution trace."""
        self.program_counter = 0
        self.halted = False
        self.steps = 0
        trace = []

        while not self.halted and self.program_counter < len(self.program):
            if self.steps >= self.max_steps:
                trace.append({"step": self.steps, "error": "max_steps exceeded"})
                break

            opcode, operand = self.program[self.program_counter]
            self.steps += 1

            if opcode == "PUSH":
                try:
                    value = int(operand)
                except ValueError:
                    value = operand
                self.stack.append(value)
                trace.append({"step": self.steps, "op": "PUSH", "value": value, "stack_depth": len(self.stack)})

            elif opcode == "STORE":
                if self.stack:
                    self.memory[operand] = self.stack.pop()
                    trace.append({"step": self.steps, "op": "STORE", "key": operand})

            elif opcode == "LOAD":
                if operand in self.memory:
                    self.stack.append(self.memory[operand])
                    trace.append({"step": self.steps, "op": "LOAD", "key": operand})
                else:
                    trace.append({"step": self.steps, "op": "LOAD", "error": f"key '{operand}' not in memory"})

            elif opcode == "ADD":
                if len(self.stack) >= 2:
                    b = self.stack.pop()
                    a = self.stack.pop()
                    result = a + b
                    self.stack.append(result)
                    trace.append({"step": self.steps, "op": "ADD", "result": result})

            elif opcode == "SUB":
                if len(self.stack) >= 2:
                    b = self.stack.pop()
                    a = self.stack.pop()
                    result = a - b
                    self.stack.append(result)
                    trace.append({"step": self.steps, "op": "SUB", "result": result})

            elif opcode == "EMIT":
                if self.stack:
                    value = self.stack[-1]
                    self.output.append(value)
                    trace.append({"step": self.steps, "op": "EMIT", "value": value})

            elif opcode == "HALT":
                self.halted = True
                trace.append({"step": self.steps, "op": "HALT"})

            else:
                trace.append({"step": self.steps, "op": opcode, "error": f"unknown opcode '{opcode}'"})

            self.program_counter += 1

        return {
            "steps": self.steps,
            "output": self.output,
            "stack": self.stack,
            "memory": dict(self.memory),
            "halted": self.halted,
            "trace": trace,
        }

    def reset(self):
        """Reset VM state."""
        self.stack.clear()
        self.memory.clear()
        self.output.clear()
        self.program_counter = 0
        self.halted = False
        self.steps = 0


class HexGrammarCompiler:
    """Compiles HEX grammar directives into metadata structures."""

    def __init__(self):
        self.opcodes = {}
        self.topologies = set()
        self.channels = set()
        self.anomalies = set()
        self.compiled = False

    def compile(self, grammar_text: str) -> dict:
        """Parse a HEX grammar file and extract directives."""
        for line in grammar_text.splitlines():
            line = line.split("#")[0].strip()
            if not line:
                continue
            parts = line.split(None, 2)
            if len(parts) < 2:
                continue

            directive = parts[0].upper()
            rest = line[len(parts[0]):].strip()

            if directive == "OPCODE":
                # Parse: OPCODE PUSH <value> # description
                name_match = re.match(r"(\w+)", rest)
                if name_match:
                    name = name_match.group(1).upper()
                    desc = rest[name_match.end():].strip().lstrip("# ").strip()
                    self.opcodes[name] = {"description": desc}

            elif directive == "TOPOLOGY":
                for t in rest.split("|"):
                    self.topologies.add(t.strip())

            elif directive == "CHANNEL":
                for c in rest.split("|"):
                    self.channels.add(c.strip())

            elif directive == "ANOMALY":
                for a in rest.split("|"):
                    self.anomalies.add(a.strip())

        self.compiled = True
        return self.to_dict()

    def to_dict(self) -> dict:
        return {
            "opcodes": self.opcodes,
            "topologies": sorted(self.topologies),
            "channels": sorted(self.channels),
            "anomalies": sorted(self.anomalies),
        }


def run_all_grammars() -> dict:
    """Load and compile all HEX grammar files."""
    grammars_dir = ROOT / "ixpansion" / "src" / "hex" / "grammars"
    results = {}
    if grammars_dir.exists():
        for gf in grammars_dir.glob("*.hexg"):
            compiler = HexGrammarCompiler()
            results[gf.stem] = compiler.compile(gf.read_text())
    return results


def run_all_scripts() -> dict:
    """Execute all HEX scripts and collect results."""
    scripts_dir = ROOT / "ixpansion" / "src" / "hex" / "scripts"
    results = {}
    if scripts_dir.exists():
        for sf in scripts_dir.glob("*.hex"):
            vm = HexVM()
            vm.load_file(sf)
            result = vm.execute()
            results[sf.stem] = result
    return results


def demo():
    """Run the full HEX VM demo."""
    grammars = run_all_grammars()
    scripts = run_all_scripts()

    return {
        "hex_vm": "HEX Virtual Machine v1.0",
        "grammars": grammars,
        "script_results": scripts,
        "grammar_count": len(grammars),
        "script_count": len(scripts),
        "total_output": sum(len(s["output"]) for s in scripts.values()),
    }


def main():
    import json
    result = demo()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
