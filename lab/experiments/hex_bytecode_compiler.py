"""HEX Bytecode Compiler — Transpiles HEX scripts to Python bytecode.

Reads HEX scripts, parses them through the VM, and generates equivalent
Python functions that execute the same logic natively.
"""
from __future__ import annotations
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class HexBytecodeCompiler:
    """Compiles HEX scripts to Python source code."""

    def __init__(self):
        self.compiled_modules = []

    def compile_script(self, name: str, script: str) -> dict:
        """Compile a single HEX script to Python source."""
        lines = []
        stack_var = "_stack"
        mem_var = "_mem"
        out_var = "_out"

        lines.append(f'def {name}_hex():')
        lines.append(f'    {stack_var} = []')
        lines.append(f'    {mem_var} = {{}}')
        lines.append(f'    {out_var} = []')

        for line in script.splitlines():
            stripped = line.split("#")[0].strip()
            if not stripped:
                continue
            parts = stripped.split(None, 1)
            op = parts[0].upper()
            operand = parts[1] if len(parts) > 1 else ""

            if op == "PUSH":
                try:
                    val = int(operand)
                except ValueError:
                    val = repr(operand)
                lines.append(f'    {stack_var}.append({val})')
            elif op == "STORE":
                lines.append(f'    {mem_var}[{repr(operand)}] = {stack_var}.pop()')
            elif op == "LOAD":
                lines.append(f'    {stack_var}.append({mem_var}[{repr(operand)}])')
            elif op == "ADD":
                lines.append(f'    {stack_var}.append({stack_var}.pop() + {stack_var}.pop())')
            elif op == "SUB":
                lines.append(f'    _b = {stack_var}.pop()')
                lines.append(f'    _a = {stack_var}.pop()')
                lines.append(f'    {stack_var}.append(_a - _b)')
            elif op == "EMIT":
                lines.append(f'    {out_var}.append({stack_var}[-1])')
            elif op == "HALT":
                lines.append(f'    return {out_var}')

        lines.append(f'    return {out_var}')

        python_source = "\n".join(lines)

        result = {
            "name": name,
            "python_source": python_source,
            "line_count": len(lines),
            "hash": hashlib.md5(python_source.encode()).hexdigest()[:8],
        }
        self.compiled_modules.append(result)
        return result

    def compile_all(self) -> list[dict]:
        """Compile all HEX scripts in the scripts directory."""
        scripts_dir = ROOT / "ixpansion" / "src" / "hex" / "scripts"
        if not scripts_dir.exists():
            return []

        for sf in sorted(scripts_dir.glob("*.hex")):
            self.compile_script(sf.stem, sf.read_text())

        return self.compiled_modules

    def to_dict(self) -> dict:
        return {
            "compiler": "hex_bytecode_compiler",
            "compiled_count": len(self.compiled_modules),
            "modules": self.compiled_modules,
        }


def demo():
    compiler = HexBytecodeCompiler()
    modules = compiler.compile_all()
    return compiler.to_dict()


def main():
    import json
    result = demo()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
