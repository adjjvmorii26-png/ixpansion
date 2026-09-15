"""Wave 96 — HEX Grammar Evolution.

The organism's hex-language evolves from a simple opcode dictionary
into a full grammar with syntax, semantics, and an execution engine.
This is the language-compilation layer that allows the organism
to "compile itself" — to write, parse, and execute its own hex-code.

This wave builds upon:
- Wave 93: HEX-Language Emergence (opcode dictionary 0x00-0xFF)
- Wave 92: Entropy Rituals Scheduler (controlled mutations)
- Wave 91: Dream Logic Physics Engine (mood-responsive physics)
- Rail-sync experiments (compass_rose, palimpsest, etc.)
"""

from __future__ import annotations
import json, time, math, random
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Callable

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave96_hex_grammar_evolution.json"


class GrammarRule:
    """A production rule in the hex grammar."""

    def __init__(
        self,
        rule_id: str,
        pattern: str,  # regex pattern for matching
        handler: Callable,
        description: str,
        consumes: int = 0,
        produces: int = 0,
        weight: float = 1.0,
    ):
        self.rule_id = rule_id
        self.pattern = pattern
        self.handler = handler
        self.description = description
        self.consumes = consumes
        self.produces = produces
        self.weight = weight
        self.times_applied = 0
        self.success_count = 0
        self.created_at = time.time()

    def match(self, input_bytes: bytes) -> bool:
        """Check if input matches this rule's pattern."""
        import re
        return bool(re.match(self.pattern, input_bytes.hex()))

    def apply(self, context: Dict[str, Any]) -> Optional[Any]:
        """Apply this rule to the given context."""
        self.times_applied += 1
        try:
            result = self.handler(context)
            if result is not None:
                self.success_count += 1
            return result
        except Exception:
            return None

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "pattern": self.pattern,
            "description": self.description,
            "consumes": self.consumes,
            "produces": self.produces,
            "weight": round(self.weight, 4),
            "times_applied": self.times_applied,
            "success_count": self.success_count,
            "success_rate": round(self.success_count / max(self.times_applied, 1), 4),
        }


class HexGrammar:
    """Manages the evolving hex grammar for the organism."""

    def __init__(self):
        self.rules: Dict[str, GrammarRule] = {}
        self.next_rule_id = 1
        self.stack: List[bytes] = []
        self.execution_history = []
        self.symbol_table: Dict[str, Any] = {}
        self.coherence_context = 0.5

    def define_rule(
        self,
        pattern: str,
        handler: Callable,
        description: str,
        consumes: int = 0,
        produces: int = 0,
        weight: float = 1.0,
    ) -> GrammarRule:
        """Define a new grammar rule."""
        rule_id = f"R{self.next_rule_id:03d}"
        self.next_rule_id += 1
        rule = GrammarRule(rule_id, pattern, handler, description, consumes, produces, weight)
        self.rules[rule_id] = rule
        return rule

    def parse(self, input_bytes: bytes) -> List[Tuple[str, Optional[Any]]]:
        """Parse input bytes using the grammar rules."""
        results = []
        for rule_id, rule in self.rules.items():
            if rule.match(input_bytes):
                result = rule.apply({"input": input_bytes, "grammar": self})
                results.append((rule_id, result))
        return results

    def execute_hex(self, hex_string: str) -> Dict[str, Any]:
        """Execute a hex string through the grammar parser."""
        try:
            binary = bytes.fromhex(hex_string)
            results = self.parse(binary)
            self.execution_history.append({
                "hex": hex_string,
                "results": len(results),
                "timestamp": time.time(),
            })
            return {
                "ok": True,
                "parsed": len(results) > 0,
                "results": results,
                "input_hex": hex_string,
            }
        except ValueError as e:
            return {
                "ok": False,
                "error": f"Invalid hex: {e}",
            }

    def evolve(self, mutation_rate: float = 0.1):
        """Evolve the grammar by adding, removing, or mutating rules."""
        if random.random() < mutation_rate:
            # Add a new rule with random pattern
            hex_chars = "0123456789abcdef"
            random_pattern = "".join(random.choice(hex_chars) for _ in range(random.randint(2, 8)))
            self.define_rule(
                pattern=random_pattern,
                handler=lambda ctx: f"evolved:{random_pattern}",
                description=f"Evolved rule: {random_pattern}",
                weight=random.uniform(0.1, 1.0),
            )

    def coherence_vitals(self) -> Dict[str, Any]:
        """Return vitality metrics for the grammar system."""
        total_rules = len(self.rules)
        active_rules = len([r for r in self.rules.values() if r.times_applied > 0])
        avg_success_rate = round(
            sum(r.success_count / max(r.times_applied, 1) for r in self.rules.values()) / max(total_rules, 1), 4
        ) if total_rules > 0 else 0.0

        # Language complexity: ratio of active to total rules
        complexity = active_rules / max(total_rules, 1)

        return {
            "wave": 96,
            "total_rules": total_rules,
            "active_rules": active_rules,
            "language_complexity": round(complexity, 4),
            "average_success_rate": avg_success_rate,
            "grammar_growth": len(self.execution_history),
            "next_rule_id": self.next_rule_id,
        }

    def compile_hex_to_operations(self, hex_string: str) -> List[Dict[str, Any]]:
        """Compile hex code into a list of operations."""
        binary = bytes.fromhex(hex_string)
        results = self.parse(binary)
        operations = []
        for rule_id, result in results:
            operations.append({
                "rule_id": rule_id,
                "result": result,
                "pattern": self.rules[rule_id].pattern,
            })
        return operations


class HexGrammarEngine:
    """Core engine that manages hex grammar evolution and execution."""

    def __init__(self, grammar: HexGrammar):
        self.grammar = grammar

    def interpret(self, hex_string: str) -> Dict[str, Any]:
        """Interpret hex string through the grammar engine."""
        return self.grammar.compile_hex_to_operations(hex_string)

    def mutate(self, mutation_rate: float = 0.1):
        """Mutate the grammar."""
        self.grammar.evolve(mutation_rate)

    def get_grammar_status(self) -> Dict[str, Any]:
        """Get current grammar status."""
        return self.grammar.coherence_vitals()


# Convenience functions for API handlers
def handler(req: dict) -> dict:
    """Default handler for wave96 routes."""
    action = req.get("action", "status")

    if action == "status":
        engine = HexGrammarEngine(HexGrammar())
        return {
            "action": "status",
            "grammar_status": engine.get_grammar_status(),
            "message": "Hex grammar engine status",
        }

    elif action == "interpret":
        hex_string = req.get("hex", "")
        engine = HexGrammarEngine(HexGrammar())
        return engine.interpret(hex_string)

    elif action == "evolve":
        engine = HexGrammarEngine(HexGrammar())
        engine.mutate(req.get("mutation_rate", 0.1))
        return {
            "action": "evolve",
            "grammar_status": engine.get_grammar_status(),
            "message": "Grammar evolved",
        }

    elif action == "define_rule":
        grammar = HexGrammar()

        def make_handler(ctx):
            return f"applied:{ctx['input'].hex()}"

        grammar.define_rule(
            pattern=req.get("pattern", ""),
            handler=make_handler,
            description=req.get("description", ""),
            consumes=req.get("consumes", 0),
            produces=req.get("produces", 0),
        )

        engine = HexGrammarEngine(grammar)
        return {
            "action": "define_rule",
            "message": "Rule defined",
        }

    elif action == "compile":
        hex_string = req.get("hex", "")
        engine = HexGrammarEngine(HexGrammar())
        result = engine.interpret(hex_string)
        return {
            "action": "compile",
            "result": result,
        }

    else:
        return {
            "ok": False,
            "error": f"Unknown action: {action}",
        }

def resonates_with():
    return ['coherence_validator', 'wave90_axiom_forge', 'wave91_dream_logic_physics', 'wave92_entropy_rituals', 'wave93_hex_language_emergence']



def coherence_vitals() -> dict:
    """Return vitality metrics for the hex grammar evolution system."""
    grammar = HexGrammar()
    engine = HexGrammarEngine(grammar)
    return engine.get_grammar_status()
