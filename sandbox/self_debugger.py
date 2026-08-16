"""Self Debugger: the organism's immune system.

Given a cell that fails its harness, this module tries, in order of
increasing cost:

1. **Pattern heuristics** -- a small library of "common bug" rewrites
   (off-by-one comparisons, append/extend confusion, missing final flush,
   truthiness inversions) applied directly and re-tested.
2. **Evolutionary search** -- random mutations (from ``idea_lab``) hill-climbed
   over a bounded number of generations, keeping only strictly-better or
   equal-and-simpler variants.
3. **Optional LLM-assisted repair** -- if a bridge is configured, the failing
   code, error output, and harness are shown to the model and asked for a
   corrected version; used only if it compiles and truly improves fitness.

Every attempt is scored purely by re-running the harness in a fresh
``World`` cell, so nothing here trusts static analysis alone -- fitness is
always behavioral.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass
from typing import List, Optional

from idea_lab import IdeaLab
from llm_bridge import LLMBridge
from world_builder import ExecutionResult, World


@dataclass
class RepairAttempt:
    strategy: str
    code: str
    result: ExecutionResult


@dataclass
class RepairReport:
    healed: bool
    best_code: str
    best_result: ExecutionResult
    attempts: List[RepairAttempt]
    strategy_used: Optional[str]


_HEURISTIC_PATCHES = [
    ("off-by-one <=/<", lambda code: code.replace(" < ", " <= ", 1)),
    ("off-by-one >=/>", lambda code: code.replace(" > ", " >= ", 1)),
    ("append->extend", lambda code: code.replace(".append(", ".extend(", 1)),
    ("extend->append", lambda code: code.replace(".extend(", ".append(", 1)),
    ("== to >=", lambda code: code.replace(" == ", " >= ", 1)),
    ("truthiness flip", lambda code: re.sub(r"\bif not (\w)", r"if \1", code, count=1)),
]


def _add_lowercase_call(code: str) -> str:
    """Heuristic: many "case sensitivity" bugs are fixed by lowering the input."""
    match = re.search(r"re\.findall\(([^,]+),\s*text\)", code)
    if match:
        return code.replace(match.group(0), match.group(0).replace("text)", "text.lower())"))
    if "for c in text if c.isalnum()" in code and ".lower()" not in code:
        return code.replace(
            "for c in text if c.isalnum()",
            "for c in text.lower() if c.isalnum()",
        )
    return code


def _restore_final_append(code: str) -> str:
    """Heuristic for loops that build a running accumulator but forget the
    final flush before returning (a classic run-length-encoding style bug).

    Finds the last ``accumulator.append(...)`` statement inside the function
    body and, if it is not already the statement immediately preceding the
    final ``return``, re-inserts a copy of it -- reindented to the return
    statement's level -- right before that return.
    """
    lines = code.split("\n")
    return_index = None
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip().startswith("return "):
            return_index = i
            break
    if return_index is None or return_index == 0:
        return code

    append_index = None
    for i in range(return_index - 1, -1, -1):
        if re.search(r"\w+\.append\(", lines[i]):
            append_index = i
            break
    if append_index is None:
        return code

    return_indent = lines[return_index][: len(lines[return_index]) - len(lines[return_index].lstrip())]
    flush_statement = return_indent + lines[append_index].strip()

    if lines[return_index - 1].strip() == flush_statement.strip():
        return code  # already flushed right before the return

    new_lines = lines[:return_index] + [flush_statement] + lines[return_index:]
    return "\n".join(new_lines)


class SelfDebugger:
    """Coordinates heuristic, evolutionary, and optional LLM repair passes."""

    def __init__(
        self,
        world: World,
        idea_lab: Optional[IdeaLab] = None,
        rng: Optional[random.Random] = None,
        llm: Optional[LLMBridge] = None,
        max_generations: int = 24,
        population_size: int = 6,
    ):
        self.world = world
        self.idea_lab = idea_lab or IdeaLab()
        self.rng = rng or random.Random()
        self.llm = llm or LLMBridge()
        self.max_generations = max_generations
        self.population_size = population_size

    def _score(self, code: str, harness: str) -> ExecutionResult:
        return self.world.run_harness(code, harness)

    def heal(self, code: str, harness: str, initial_result: Optional[ExecutionResult] = None) -> RepairReport:
        attempts: List[RepairAttempt] = []
        best_code = code
        best_result = initial_result or self._score(code, harness)
        if best_result.solved:
            return RepairReport(True, best_code, best_result, attempts, None)

        strategy_used: Optional[str] = None

        heuristic_result = self._run_heuristics(best_code, harness, attempts)
        if heuristic_result is not None:
            best_code, best_result = heuristic_result
            strategy_used = "heuristic"
            if best_result.solved:
                return RepairReport(True, best_code, best_result, attempts, strategy_used)

        evolved = self._run_evolution(best_code, best_result, harness, attempts)
        if evolved is not None:
            best_code, best_result = evolved
            strategy_used = "evolution"
            if best_result.solved:
                return RepairReport(True, best_code, best_result, attempts, strategy_used)

        llm_result = self._run_llm_repair(best_code, best_result, harness, attempts)
        if llm_result is not None:
            best_code, best_result = llm_result
            strategy_used = "llm"

        return RepairReport(best_result.solved, best_code, best_result, attempts, strategy_used)

    def _run_heuristics(self, code: str, harness: str, attempts: List[RepairAttempt]):
        candidates = [patch(code) for _, patch in _HEURISTIC_PATCHES]
        candidates.append(_add_lowercase_call(code))
        candidates.append(_restore_final_append(code))
        best_code = code
        best_score = self._score(code, harness).fitness
        found = False
        for candidate in candidates:
            if candidate == code or not World.compiles(candidate):
                continue
            result = self._score(candidate, harness)
            attempts.append(RepairAttempt("heuristic", candidate, result))
            if result.fitness > best_score:
                best_code, best_score = candidate, result.fitness
                found = True
                if result.solved:
                    return best_code, result
        if found:
            return best_code, self._score(best_code, harness)
        return None

    def _run_evolution(self, code: str, current_result: ExecutionResult, harness: str, attempts: List[RepairAttempt]):
        population = [code]
        best_code = code
        best_result = current_result
        for generation in range(self.max_generations):
            children = []
            for parent in population:
                for _ in range(max(1, self.population_size // max(1, len(population)))):
                    children.append(self.idea_lab.mutate(parent))
            if len(population) >= 2:
                a, b = self.rng.sample(population, 2)
                children.append(self.idea_lab.crossover(a, b))

            scored = []
            for child in children:
                if not World.compiles(child):
                    continue
                result = self._score(child, harness)
                attempts.append(RepairAttempt(f"evolution-gen{generation}", child, result))
                scored.append((result.fitness, len(child), child, result))

            if not scored:
                continue
            scored.sort(key=lambda item: (-item[0], item[1]))
            top_fitness, _, top_code, top_result = scored[0]

            if top_fitness > best_result.fitness or (
                top_fitness == best_result.fitness and len(top_code) < len(best_code)
            ):
                best_code, best_result = top_code, top_result

            if best_result.solved:
                return best_code, best_result

            survivors = [item[2] for item in scored[: max(2, self.population_size // 2)]]
            population = list({*survivors, best_code})

        if best_result.fitness > current_result.fitness:
            return best_code, best_result
        return None

    def _run_llm_repair(self, code: str, current_result: ExecutionResult, harness: str, attempts: List[RepairAttempt]):
        if not self.llm.available:
            return None
        error_hint = ""
        if current_result.result:
            error_hint = str(current_result.result.get("errors") or current_result.result.get("error") or "")
        prompt = (
            "This Python module fails some tests. Return ONLY the corrected "
            "full module in a single ```python code block, no explanation.\n\n"
            f"Current code:\n```python\n{code}\n```\n\n"
            f"Test failures: {error_hint}\n"
            f"Test harness for context:\n```python\n{harness}\n```\n"
        )
        response = self.llm.chat(
            system="You are a precise Python bug-fixing engine for an automated sandbox.",
            user=prompt,
        )
        if not response:
            return None
        fixed = LLMBridge.extract_code(response)
        if not fixed or not World.compiles(fixed):
            return None
        result = self._score(fixed, harness)
        attempts.append(RepairAttempt("llm", fixed, result))
        if result.fitness > current_result.fitness:
            return fixed, result
        return None
