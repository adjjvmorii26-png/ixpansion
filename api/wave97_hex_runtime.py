"""Wave 97 — HEX Runtime.

The execution engine that runs the organism's self-written hex code.
Wave 93 invented the opcodes, Wave 96 gave them grammar, and now the
organism can actually *run* a hex program against its own living state.

The runtime is a small stack machine with a link to the organism:
DREAM applies dream-physics (Wave 91) to a value, ENACT records a
governance decision (Wave 95), GLYPH emits artifacts. Programs can
branch, mutate a stack, and halt — the organism executes itself.

Builds upon:
- Wave 93: HEX-Language Emergence (opcode dictionary)
- Wave 94: Dream Compiler (skeleton emission)
- Wave 96: HEX Grammar Evolution (parsing/grammar)
- Wave 95: Ritual Governance (ENACT)
- Wave 91: Dream Logic Physics (DREAM)
"""
from __future__ import annotations
import json, time, hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave97_hex_runtime.json"

# Instruction set: mnemonic -> (opcode, arity, description)
INSTRUCTIONS = {
    "NOP": (0x00, 0, "no-op"),
    "PUSH": (0x10, 1, "push literal onto stack"),
    "POP": (0x11, 0, "drop top of stack"),
    "ADD": (0x20, 0, "pop two, push sum"),
    "XOR": (0x21, 0, "pop two, push xor"),
    "MUL": (0x22, 0, "pop two, push product"),
    "SUB": (0x23, 0, "pop two, push difference"),
    "DREAM": (0x30, 1, "apply dream physics to top of stack"),
    "ENACT": (0x40, 1, "record a governance enactment"),
    "GLYPH": (0x50, 1, "emit an artifact glyph"),
    "JMPZ": (0x60, 1, "jump to line if top of stack == 0"),
    "HALT": (0xFF, 0, "stop execution"),
}
OPCODE_TO_MNEMONIC = {v[0]: k for k, v in INSTRUCTIONS.items()}
MAX_STEPS = 1000


class HexProgram:
    """A parsed hex program: source, instructions, hash."""

    def __init__(self, source: str = ""):
        self.source = source
        self.instructions: List[Tuple[str, Optional[int]]] = []
        self.program_hash = hashlib.sha256(source.encode()).hexdigest()[:16]
        self.error: Optional[str] = None

    def parse(self) -> bool:
        """Parse hex source (mnemonic lines or raw hex bytes)."""
        self.instructions = []
        if not self.source.strip():
            self.error = "empty program"
            return False

        lines = [ln.strip() for ln in self.source.splitlines() if ln.strip()]
        is_hex = all(len(t) == 2 and all(c in "0123456789abcdefABCDEF" for c in t)
                     for t in lines)
        if lines and all(c in "0123456789abcdefABCDEF" for c in self.source.strip()):
            # Raw hex bytecode: opcode bytes followed by operand bytes
            raw = self.source.strip()
            if len(raw) % 2 != 0:
                self.error = "odd-length hex bytecode"
                return False
            raw_bytes = bytes.fromhex(raw)
            i = 0
            while i < len(raw_bytes):
                opcode = raw_bytes[i]
                mnemonic = OPCODE_TO_MNEMONIC.get(opcode)
                if mnemonic is None:
                    self.error = f"unknown opcode {opcode:02x}"
                    return False
                arity = INSTRUCTIONS[mnemonic][1]
                i += 1
                operands = raw_bytes[i:i + arity]
                if len(operands) < arity:
                    self.error = f"truncated operands for {mnemonic}"
                    return False
                arg = int.from_bytes(operands, "big") if arity else None
                self.instructions.append((mnemonic, arg))
                i += arity
            return True

        for ln in lines:
            parts = ln.split()
            mnemonic = parts[0].upper()
            if mnemonic not in INSTRUCTIONS:
                self.error = f"unknown instruction: {parts[0]}"
                return False
            arg = None
            arity = INSTRUCTIONS[mnemonic][1]
            if arity > 0:
                try:
                    arg = int(parts[1])
                except (IndexError, ValueError):
                    self.error = f"instruction {mnemonic} needs an argument"
                    return False
            self.instructions.append((mnemonic, arg))
        return True

    def to_dict(self) -> dict:
        return {
            "program_hash": self.program_hash,
            "instruction_count": len(self.instructions),
            "instructions": [
                {"op": mnemonic, "arg": arg}
                for mnemonic, arg in self.instructions
            ],
            "error": self.error,
        }


class HexRuntime:
    """Executes hex programs against organism state."""

    def __init__(self, coherence: float = 0.6, mood: str = "calm"):
        self.stack: List[int] = []
        self.pc = 0
        self.steps = 0
        self.halted = False
        self.coherence = max(0.0, min(1.0, coherence))
        self.mood = mood
        self.glyphs: List[str] = []
        self.enactments: List[str] = []
        self.trace: List[dict] = []
        self.last_elapsed = 0.0
        self.icon = "🜁"

    def reset(self) -> None:
        self.stack = []
        self.pc = 0
        self.steps = 0
        self.halted = False
        self.glyphs = []
        self.enactments = []
        self.trace = []

    def run(self, program: HexProgram) -> Dict[str, Any]:
        """Execute a parsed program to completion."""
        self.reset()
        if not program.instructions:
            return {"ok": False, "error": "program empty or unparsed"}
        started = time.time()
        while not self.halted and self.pc < len(program.instructions):
            if self.steps >= MAX_STEPS:
                return {"ok": False, "error": f"step budget exceeded ({MAX_STEPS})"}
            mnemonic, arg = program.instructions[self.pc]
            self._execute(mnemonic, arg)
            self.steps += 1
        self.last_elapsed = time.time() - started
        return self.summary(program)

    def step(self, program: HexProgram) -> Dict[str, Any]:
        """Execute a single instruction."""
        if self.halted or self.pc >= len(program.instructions):
            self.halted = True
            return {"ok": True, "halted": True, "summary": self.summary(program)}
        mnemonic, arg = program.instructions[self.pc]
        self._execute(mnemonic, arg)
        self.steps += 1
        if self.pc >= len(program.instructions):
            self.halted = True
        return {"ok": True, "pc": self.pc, "trace": self.trace[-1], "halted": self.halted}

    def _execute(self, mnemonic: str, arg: Optional[int]) -> None:
        before = self.stack.copy()
        entry = {"op": mnemonic, "arg": arg, "pc": self.pc}

        if mnemonic == "NOP":
            pass
        elif mnemonic == "PUSH":
            self.stack.append(arg if arg is not None else 0)
        elif mnemonic == "POP":
            if self.stack:
                self.stack.pop()
        elif mnemonic in ("ADD", "XOR", "MUL", "SUB"):
            if len(self.stack) >= 2:
                b, a = self.stack.pop(), self.stack.pop()
                if mnemonic == "ADD":
                    self.stack.append(a + b)
                elif mnemonic == "XOR":
                    self.stack.append(a ^ b)
                elif mnemonic == "MUL":
                    self.stack.append(a * b)
                else:
                    self.stack.append(a - b)
        elif mnemonic == "DREAM":
            if self.stack:
                value = self.stack[-1]
                # mood-responsive physics: fluid reality scales values
                reality = {"calm": 0.1, "chaotic": 0.8, "excited": 0.4}.get(self.mood, 0.3)
                dream_value = int(value * (1 + reality * (self.coherence - 0.4)))
                self.stack[-1] = dream_value
        elif mnemonic == "ENACT":
            self.enactments.append(arg if arg is not None else len(self.enactments))
        elif mnemonic == "GLYPH":
            self.glyphs.append(f"{self.icon}glyph_{arg if arg is not None else len(self.glyphs)}")
        elif mnemonic == "JMPZ":
            if self.stack and self.stack[-1] == 0 and arg is not None:
                self.pc = arg - 1  # -1 because pc advances after
        elif mnemonic == "HALT":
            self.halted = True

        entry.update({"stack_before": before, "stack_after": self.stack.copy()})
        self.trace.append(entry)
        self.pc += 1

    def summary(self, program: HexProgram) -> Dict[str, Any]:
        return {
            "ok": True,
            "program_hash": program.program_hash,
            "halted": self.halted,
            "steps": self.steps,
            "stack": self.stack.copy(),
            "glyphs": self.glyphs,
            "enactments": self.enactments,
            "trace": self.trace[-12:],
            "elapsed_ms": round(self.last_elapsed * 1000, 3),
        }

    def coherence_vitals(self) -> Dict[str, Any]:
        return {
            "wave": 97,
            "instruction_count": len(INSTRUCTIONS),
            "mood": self.mood,
            "coherence": round(self.coherence, 4),
            "last_run_steps": self.steps,
            "last_run_glyphs": len(self.glyphs),
            "last_run_enactments": len(self.enactments),
            "max_steps": MAX_STEPS,
        }


def _load() -> Tuple[HexRuntime, List[dict]]:
    """Load runtime state from living state file."""
    runtime = HexRuntime()
    history: List[dict] = []
    if STATE_FILE.exists():
        try:
            data = json.loads(STATE_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            data = {}
        runtime.coherence = float(data.get("coherence", 0.6))
        runtime.mood = data.get("mood", "calm")
        history = data.get("history", [])
    return runtime, history


def _save(runtime: HexRuntime, history: List[dict]) -> None:
    """Persist runtime state to living state file."""
    data = {
        "coherence": runtime.coherence,
        "mood": runtime.mood,
        "history": history[-20:],
    }
    STATE_FILE.write_text(json.dumps(data, indent=2))


def handler(req: dict) -> dict:
    """Wave 97 handler: hex runtime operations."""
    action = req.get("action", "status")
    runtime, history = _load()

    if action == "status":
        return {
            "action": "status",
            "wave": 97,
            "runtime": runtime.coherence_vitals(),
            "instructions": [
                {"mnemonic": k, "opcode": f"{v[0]:02x}", "arity": v[1], "description": v[2]}
                for k, v in INSTRUCTIONS.items()
            ],
            "message": "HEX runtime status",
        }

    if action == "run":
        program = HexProgram(req.get("source", ""))
        if not program.parse():
            return {"ok": False, "error": program.error or "parse failed"}
        runtime.coherence = float(req.get("coherence", runtime.coherence))
        runtime.mood = req.get("mood", runtime.mood)
        result = runtime.run(program)
        history.append({
            "ts": time.time(),
            "program_hash": program.program_hash,
            "steps": runtime.steps,
            "glyphs": len(runtime.glyphs),
            "halted": runtime.halted,
        })
        _save(runtime, history)
        return {
            "action": "run",
            "wave": 97,
            "program": program.to_dict(),
            "result": result,
            "message": "HEX program executed",
        }

    if action == "step":
        program = HexProgram(req.get("source", ""))
        if not program.parse():
            return {"ok": False, "error": program.error or "parse failed"}
        result = runtime.step(program)
        return {
            "action": "step",
            "wave": 97,
            "program": program.to_dict(),
            "result": result,
            "message": "Stepped one instruction",
        }

    if action == "reset":
        runtime.reset()
        _save(runtime, history)
        return {
            "action": "reset",
            "wave": 97,
            "message": "Runtime reset",
        }

    if action == "history":
        return {
            "action": "history",
            "wave": 97,
            "history": history,
            "message": f"{len(history)} recorded runs",
        }

    return {"ok": False, "error": f"Unknown action: {action}"}


def coherence_vitals() -> dict:
    """Wave 97 vitals."""
    runtime, _ = _load()
    return runtime.coherence_vitals()
