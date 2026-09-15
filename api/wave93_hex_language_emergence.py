"""Wave 93 — HEX-Language Emergence.

The organism invents a machine-language dialect that evolves across waves.
This hex-encoded language becomes the genetic code for new modules,
allowing the organism to "write itself" in its native aesthetic.
"""

from __future__ import annotations
import json, time, math, random
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave93_hex_language_emergence.json"


class HexOpcode:
    """A single hex opcode in the organism's emerging language."""

    OPCODE_SPACE = 256  # 0x00 - 0xFF

    def __init__(self, opcode: int, mnemonic: str, description: str,
                 latency: float = 1.0, consumes: int = 1, produces: int = 1):
        if not 0 <= opcode < self.OPCODE_SPACE:
            raise ValueError(f"Opcode must be 0-{self.OPCODE_SPACE - 1}, got {opcode}")
        self.opcode = opcode
        self.mnemonic = mnemonic
        self.description = description
        self.latency = latency
        self.consumes = consumes  # Number of stack items consumed
        self.produces = produces  # Number of stack items produced
        self.created_at = time.time()
        self.usage_count = 0
        self.amendment_history = []

    def execute(self, stack: List[int]) -> Tuple[List[int], Optional[int]]:
        """Execute opcode on a stack, returning new stack and output."""
        if len(stack) < self.consumes:
            raise ValueError(f"Stack underflow: need {self.consumes}, have {len(stack)}")

        # Consume inputs
        inputs = stack[:self.consumes]
        stack = stack[self.consumes:]

        # Produce outputs based on opcode type
        outputs = []
        if self.produces >= 1:
            # Simple: produce a hash-based value
            input_hash = int(hashlib.md5(str(inputs).encode()).hexdigest(), 16) % 256
            outputs = [input_hash]
        elif self.produces >= 2:
            outputs = [inputs[0] ^ inputs[1], (inputs[0] + inputs[1]) % 256]

        # Update usage
        self.usage_count += 1

        # New stack = remaining + outputs
        new_stack = stack + outputs
        return new_stack, outputs[0] if outputs else None

    def to_dict(self) -> dict:
        return {
            "opcode": hex(self.opcode),
            "mnemonic": self.mnemonic,
            "description": self.description,
            "latency": round(self.latency, 3),
            "consumes": self.consumes,
            "produces": self.produces,
            "usage_count": self.usage_count,
        }


class HexLanguageEngine:
    """Engine that manages the evolving hex language for the organism."""

    def __init__(self):
        self.opcodes: Dict[int, HexOpcode] = {}
        self.next_opcode = 0x10  # Start after basic system opcodes
        self.stack: List[int] = []
        self.execution_history = []
        self.coherence_context = 0.5

    def define_opcode(self, mnemonic: str, description: str,
                      latency: float = 1.0, consumes: int = 1, produces: int = 1) -> HexOpcode:
        """Define a new opcode in the emerging language."""
        if self.next_opcode >= 0xFF:
            # Wrap around with amendments
            self.next_opcode = 0x01
        opcode = self.next_opcode
        self.next_opcode += 1
        opcode_obj = HexOpcode(opcode, mnemonic, description, latency, consumes, produces)
        self.opcodes[opcode] = opcode_obj
        return opcode_obj

    def execute_opcode(self, opcode_number: int, stack: List[int]) -> Tuple[List[int], Any]:
        """Execute a specific opcode on the stack."""
        opcode = self.opcodes.get(opcode_number)
        if opcode is None:
            raise ValueError(f"Unknown opcode: {hex(opcode_number)}")
        new_stack, output = opcode.execute(stack)
        self.execution_history.append({
            "opcode": opcode_number,
            "output": output,
            "timestamp": time.time(),
            "stack_size_before": len(stack),
        })
        return new_stack, output

    def generate_hex_instruction(self, complexity: float = 0.5) -> str:
        """Generate a random hex instruction based on complexity."""
        # Select opcode based on complexity weight
        weights = [opcode.latency for opcode in self.opcodes.values()]
        if not weights:
            return "00 NOP"
        total = sum(weights)
        probabilities = [w / total for w in weights]
        selected_opcode = random.choices(list(self.opcodes.keys()), weights=probabilities)[0]
        opcode = self.opcodes[selected_opcode]
        return f"{hex(selected_opcode.opcode)[2:].zfill(2)} {opcode.mnemonic}"

    def learn_from_usage(self, opcode_number: int, success: bool):
        """Learn from opcode usage patterns."""
        opcode = self.opcodes.get(opcode_number)
        if opcode:
            # Adjust latency based on success/failure
            if success:
                opcode.latency = max(0.1, opcode.latency * 0.95)  # Speed up
            else:
                opcode.latency = min(5.0, opcode.latency * 1.05)  # Slow down
            opcode.usage_count += 1

    def coherence_vitals(self) -> Dict[str, Any]:
        """Return vitality metrics for the hex language system."""
        active_opcodes = len([o for o in self.opcodes.values() if o.usage_count > 0])
        avg_latency = round(
            sum(o.latency for o in self.opcodes.values()) / max(len(self.opcodes), 1), 4
        ) if self.opcodes else 0.0
        total_usage = sum(o.usage_count for o in self.opcodes.values())

        return {
            "wave": 93,
            "active_opcodes": active_opcodes,
            "total_opcodes_defined": len(self.opcodes),
            "next_opcode_available": hex(self.next_opcode),
            "average_opcode_latency": avg_latency,
            "total_opcode_usages": total_usage,
            "language_complexity": round(
                active_opcodes / max(len(self.opcodes), 1), 4
            ),
            "emergence_score": round(active_opcodes / 256, 4),  # Max possible density
        }

    def generate_self_modifying_code(self, length: int = 16) -> str:
        """Generate self-modifying hex code that the organism can compile."""
        code_parts = []
        available = list(self.opcodes.values())
        for _ in range(length):
            if not available:
                code_parts.append("00 NOP")
                continue
            opcode = random.choice(available)
            code_parts.append(f"{hex(opcode.opcode)[2:].zfill(2)} {opcode.mnemonic}")
        return " ".join(code_parts)

def resonates_with():
    return ['coherence_validator', 'wave90_axiom_forge', 'wave91_dream_logic_physics', 'wave92_entropy_rituals', 'wave94_dream_compiler']



def handler(req: dict) -> dict:
    """Wave 93 handler: hex-language emergence operations."""
    action = req.get("action", "status")
    engine = HexLanguageEngine()

    if action == "status":
        return {
            "action": "status",
            "wave": 93,
            "language": engine.coherence_vitals(),
            "message": "HEX-language emergence status",
        }

    if action == "define":
        opcode = engine.define_opcode(
            mnemonic=req.get("mnemonic", "NOP"),
            description=req.get("description", ""),
            latency=float(req.get("latency", 1.0)),
            consumes=int(req.get("consumes", 1)),
            produces=int(req.get("produces", 1)),
        )
        return {
            "action": "define",
            "wave": 93,
            "opcode": opcode.to_dict(),
            "message": f"Opcode {hex(opcode.opcode)} defined",
        }

    if action == "generate":
        return {
            "action": "generate",
            "wave": 93,
            "code": engine.generate_self_modifying_code(
                int(req.get("length", 16))
            ),
            "message": "Self-modifying hex code generated",
        }

    return {"ok": False, "error": f"Unknown action: {action}"}


def coherence_vitals() -> dict:
    """Wave 93 vitals."""
    return HexLanguageEngine().coherence_vitals()
