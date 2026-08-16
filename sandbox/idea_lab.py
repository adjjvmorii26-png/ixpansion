"""Idea Lab: where the organism's next experiment is born.

Two responsibilities live here:

1. **Challenges** -- small, self-contained coding problems with a reference
   solution, a deliberately buggy "seed" mutation, and a generated test
   harness. These are the organism's diet; it is never left with nothing to
   chew on, even fully offline.
2. **Genetic operators** -- ``mutate`` and ``crossover`` produce new candidate
   code from existing cells so the population keeps exploring, not just
   repairing the same seed forever.

An optional LLM bridge can be asked to invent a brand-new challenge or an
extra mutation; if it is unavailable or returns something that fails to
compile, the offline path is used instead. The organism never blocks on the
network.
"""

from __future__ import annotations

import random
import re
import textwrap
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from llm_bridge import LLMBridge
from world_builder import World

_IDENTIFIER_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


@dataclass
class Challenge:
    """One coding problem: a reference solution, a buggy seed, and a harness."""

    name: str
    description: str
    reference_solution: str
    buggy_seed: str
    harness: str
    origin: str = "builtin"


def _harness(function_name: str, cases: str) -> str:
    """Build a harness that imports ``candidate`` and scores it against cases.

    ``cases`` is a snippet defining a list literal named ``CASES`` of
    ``(args_tuple, expected)`` pairs already indented for embedding.
    """
    return textwrap.dedent(
        f"""
        import json
        import traceback

        {cases}

        def _run():
            passed = 0
            errors = []
            try:
                import candidate
            except Exception as exc:  # pragma: no cover - reported to caller
                print("SANDBOX_RESULT_JSON=" + json.dumps(
                    {{"passed": 0, "total": len(CASES), "import_error": repr(exc)}}
                ))
                return
            fn = getattr(candidate, "{function_name}", None)
            if fn is None:
                print("SANDBOX_RESULT_JSON=" + json.dumps(
                    {{"passed": 0, "total": len(CASES), "error": "missing function {function_name}"}}
                ))
                return
            for args, expected in CASES:
                try:
                    got = fn(*args)
                    if got == expected:
                        passed += 1
                    else:
                        errors.append(f"{{args!r}} -> {{got!r}} (expected {{expected!r}})")
                except Exception as exc:
                    errors.append(f"{{args!r}} raised {{exc!r}}")
            print("SANDBOX_RESULT_JSON=" + json.dumps(
                {{"passed": passed, "total": len(CASES), "errors": errors[:5]}}
            ))

        _run()
        """
    ).strip() + "\n"


def _builtin_challenges() -> List[Challenge]:
    challenges: List[Challenge] = []

    challenges.append(
        Challenge(
            name="clamp",
            description="clamp(value, low, high) restricts value to [low, high].",
            reference_solution=(
                "def clamp(value, low, high):\n"
                "    if value < low:\n"
                "        return low\n"
                "    if value > high:\n"
                "        return high\n"
                "    return value\n"
            ),
            buggy_seed=(
                "def clamp(value, low, high):\n"
                "    if value < low:\n"
                "        return value\n"  # bug: should return low
                "    if value > high:\n"
                "        return high\n"
                "    return value\n"
            ),
            harness=_harness(
                "clamp",
                "CASES = [((5, 0, 10), 5), ((-3, 0, 10), 0), ((15, 0, 10), 10), "
                "((0, 0, 0), 0), ((7, 7, 7), 7)]",
            ),
        )
    )

    challenges.append(
        Challenge(
            name="is_palindrome",
            description="is_palindrome(text) ignores case and non-alphanumerics.",
            reference_solution=(
                "def is_palindrome(text):\n"
                "    cleaned = [c.lower() for c in text if c.isalnum()]\n"
                "    return cleaned == cleaned[::-1]\n"
            ),
            buggy_seed=(
                "def is_palindrome(text):\n"
                "    cleaned = [c for c in text if c.isalnum()]\n"  # bug: no lowercasing
                "    return cleaned == cleaned[::-1]\n"
            ),
            harness=_harness(
                "is_palindrome",
                "CASES = [((\"A man a plan a canal Panama\",), True), ((\"Hello\",), False), "
                "((\"\",), True), ((\"Was it a car or a cat I saw\",), True), ((\"No\",), False)]",
            ),
        )
    )

    challenges.append(
        Challenge(
            name="flatten",
            description="flatten(nested) recursively flattens a list of lists.",
            reference_solution=(
                "def flatten(nested):\n"
                "    result = []\n"
                "    for item in nested:\n"
                "        if isinstance(item, list):\n"
                "            result.extend(flatten(item))\n"
                "        else:\n"
                "            result.append(item)\n"
                "    return result\n"
            ),
            buggy_seed=(
                "def flatten(nested):\n"
                "    result = []\n"
                "    for item in nested:\n"
                "        if isinstance(item, list):\n"
                "            result.append(flatten(item))\n"  # bug: append instead of extend
                "        else:\n"
                "            result.append(item)\n"
                "    return result\n"
            ),
            harness=_harness(
                "flatten",
                "CASES = [(([1, [2, 3], [4, [5, 6]]],), [1, 2, 3, 4, 5, 6]), "
                "(([],), []), (([1, 2, 3],), [1, 2, 3]), "
                "(([[[1]]],), [1])]",
            ),
        )
    )

    challenges.append(
        Challenge(
            name="most_common",
            description="most_common(items) returns the most frequent item, ties broken by first appearance.",
            reference_solution=(
                "def most_common(items):\n"
                "    counts = {}\n"
                "    order = []\n"
                "    for item in items:\n"
                "        if item not in counts:\n"
                "            order.append(item)\n"
                "        counts[item] = counts.get(item, 0) + 1\n"
                "    best = order[0]\n"
                "    for item in order:\n"
                "        if counts[item] > counts[best]:\n"
                "            best = item\n"
                "    return best\n"
            ),
            buggy_seed=(
                "def most_common(items):\n"
                "    counts = {}\n"
                "    order = []\n"
                "    for item in items:\n"
                "        if item not in counts:\n"
                "            order.append(item)\n"
                "        counts[item] = counts.get(item, 0) + 1\n"
                "    best = order[0]\n"
                "    for item in order:\n"
                "        if counts[item] >= counts[best]:\n"  # bug: >= breaks tie order
                "            best = item\n"
                "    return best\n"
            ),
            harness=_harness(
                "most_common",
                "CASES = [(([1, 2, 2, 3],), 2), ((['a', 'b', 'a'],), 'a'), "
                "(([1, 1, 2, 2, 3],), 1), (([5],), 5)]",
            ),
        )
    )

    challenges.append(
        Challenge(
            name="run_length_encode",
            description="run_length_encode(text) compresses runs as (char, count) tuples.",
            reference_solution=(
                "def run_length_encode(text):\n"
                "    if not text:\n"
                "        return []\n"
                "    result = []\n"
                "    current = text[0]\n"
                "    count = 1\n"
                "    for ch in text[1:]:\n"
                "        if ch == current:\n"
                "            count += 1\n"
                "        else:\n"
                "            result.append((current, count))\n"
                "            current = ch\n"
                "            count = 1\n"
                "    result.append((current, count))\n"
                "    return result\n"
            ),
            buggy_seed=(
                "def run_length_encode(text):\n"
                "    if not text:\n"
                "        return []\n"
                "    result = []\n"
                "    current = text[0]\n"
                "    count = 1\n"
                "    for ch in text[1:]:\n"
                "        if ch == current:\n"
                "            count += 1\n"
                "        else:\n"
                "            result.append((current, count))\n"
                "            current = ch\n"
                "            count = 1\n"
                "    return result\n"  # bug: forgets to append the final run
            ),
            harness=_harness(
                "run_length_encode",
                "CASES = [((\"aaabbc\",), [('a', 3), ('b', 2), ('c', 1)]), "
                "((\"\",), []), ((\"x\",), [('x', 1)]), "
                "((\"aabbaa\",), [('a', 2), ('b', 2), ('a', 2)])]",
            ),
        )
    )

    challenges.append(
        Challenge(
            name="binary_search",
            description="binary_search(sorted_list, target) returns the index or -1.",
            reference_solution=(
                "def binary_search(sorted_list, target):\n"
                "    lo, hi = 0, len(sorted_list) - 1\n"
                "    while lo <= hi:\n"
                "        mid = (lo + hi) // 2\n"
                "        if sorted_list[mid] == target:\n"
                "            return mid\n"
                "        if sorted_list[mid] < target:\n"
                "            lo = mid + 1\n"
                "        else:\n"
                "            hi = mid - 1\n"
                "    return -1\n"
            ),
            buggy_seed=(
                "def binary_search(sorted_list, target):\n"
                "    lo, hi = 0, len(sorted_list) - 1\n"
                "    while lo < hi:\n"  # bug: should be <=, misses single-element / last checks
                "        mid = (lo + hi) // 2\n"
                "        if sorted_list[mid] == target:\n"
                "            return mid\n"
                "        if sorted_list[mid] < target:\n"
                "            lo = mid + 1\n"
                "        else:\n"
                "            hi = mid - 1\n"
                "    return -1\n"
            ),
            harness=_harness(
                "binary_search",
                "CASES = [(([1, 3, 5, 7, 9], 7), 3), (([1, 3, 5, 7, 9], 1), 0), "
                "(([1, 3, 5, 7, 9], 9), 4), (([1, 3, 5, 7, 9], 4), -1), (([5], 5), 0)]",
            ),
        )
    )

    challenges.append(
        Challenge(
            name="merge_intervals",
            description="merge_intervals(intervals) merges overlapping (start, end) pairs.",
            reference_solution=(
                "def merge_intervals(intervals):\n"
                "    if not intervals:\n"
                "        return []\n"
                "    ordered = sorted(intervals, key=lambda pair: pair[0])\n"
                "    merged = [list(ordered[0])]\n"
                "    for start, end in ordered[1:]:\n"
                "        if start <= merged[-1][1]:\n"
                "            merged[-1][1] = max(merged[-1][1], end)\n"
                "        else:\n"
                "            merged.append([start, end])\n"
                "    return [tuple(pair) for pair in merged]\n"
            ),
            buggy_seed=(
                "def merge_intervals(intervals):\n"
                "    if not intervals:\n"
                "        return []\n"
                "    ordered = sorted(intervals, key=lambda pair: pair[0])\n"
                "    merged = [list(ordered[0])]\n"
                "    for start, end in ordered[1:]:\n"
                "        if start < merged[-1][1]:\n"  # bug: should be <=
                "            merged[-1][1] = max(merged[-1][1], end)\n"
                "        else:\n"
                "            merged.append([start, end])\n"
                "    return [tuple(pair) for pair in merged]\n"
            ),
            harness=_harness(
                "merge_intervals",
                "CASES = [(([(1, 3), (2, 6), (8, 10)],), [(1, 6), (8, 10)]), "
                "(([(1, 4), (4, 5)],), [(1, 5)]), (([],), []), "
                "(([(1, 2), (3, 4)],), [(1, 2), (3, 4)])]",
            ),
        )
    )

    challenges.append(
        Challenge(
            name="word_frequencies",
            description="word_frequencies(text) counts lowercase words, ignoring punctuation.",
            reference_solution=(
                "import re\n\n"
                "def word_frequencies(text):\n"
                "    words = re.findall(r\"[a-zA-Z']+\", text.lower())\n"
                "    counts = {}\n"
                "    for word in words:\n"
                "        counts[word] = counts.get(word, 0) + 1\n"
                "    return counts\n"
            ),
            buggy_seed=(
                "import re\n\n"
                "def word_frequencies(text):\n"
                "    words = re.findall(r\"[a-zA-Z']+\", text)\n"  # bug: no .lower()
                "    counts = {}\n"
                "    for word in words:\n"
                "        counts[word] = counts.get(word, 0) + 1\n"
                "    return counts\n"
            ),
            harness=_harness(
                "word_frequencies",
                "CASES = [((\"The cat sat. The Cat ran!\",), {'the': 2, 'cat': 2, 'sat': 1, 'ran': 1}), "
                "((\"\",), {}), ((\"Hi Hi hi\",), {'hi': 3})]",
            ),
        )
    )

    return challenges


class IdeaLab:
    """Proposes challenges and mutates/crosses over cells for evolution."""

    def __init__(self, rng: Optional[random.Random] = None, llm: Optional[LLMBridge] = None):
        self.rng = rng or random.Random()
        self.llm = llm or LLMBridge()
        self._builtin = _builtin_challenges()

    def list_challenges(self) -> List[str]:
        return [challenge.name for challenge in self._builtin]

    def challenge_by_name(self, name: str) -> Optional[Challenge]:
        for challenge in self._builtin:
            if challenge.name == name:
                return challenge
        return None

    def propose_challenge(self, exclude: Optional[List[str]] = None) -> Challenge:
        """Pick the next challenge for the organism to work on."""
        exclude = set(exclude or [])
        pool = [c for c in self._builtin if c.name not in exclude] or self._builtin
        return self.rng.choice(pool)

    def invent_challenge_idea(self) -> Optional[str]:
        """Ask the optional LLM bridge for a fresh, one-line coding idea.

        This does not produce runnable code by itself; it seeds a note the
        engine can log. The organism's actual test cases always stay
        deterministic and offline (see ``propose_challenge``), so a flaky or
        unavailable LLM never stalls evolution.
        """
        prompt = (
            "In one short sentence, propose a small, self-contained Python "
            "function idea (name + purpose) suitable for a unit-testable "
            "coding kata. No code, just the idea."
        )
        return self.llm.chat(
            system="You are a terse creative partner for an evolving code sandbox.",
            user=prompt,
        )

    # -- genetic operators -------------------------------------------------

    @staticmethod
    def _mutate_comparison(code: str, rng: random.Random) -> str:
        swaps = [("<=", "<"), ("<", "<="), (">=", ">"), (">", ">="), ("==", "!="), ("!=", "==")]
        op_from, op_to = rng.choice(swaps)
        if op_from in code:
            idx = [i for i in range(len(code)) if code.startswith(op_from, i)]
            pos = rng.choice(idx)
            return code[:pos] + op_to + code[pos + len(op_from):]
        return code

    @staticmethod
    def _mutate_constant(code: str, rng: random.Random) -> str:
        import re as _re

        matches = list(_re.finditer(r"(?<![\w.])(\d+)(?![\w.])", code))
        if not matches:
            return code
        match = rng.choice(matches)
        original = int(match.group(1))
        delta = rng.choice([-2, -1, 1, 2])
        replacement = str(max(0, original + delta))
        return code[: match.start()] + replacement + code[match.end():]

    @staticmethod
    def _mutate_swap_lines(code: str, rng: random.Random) -> str:
        lines = code.split("\n")
        candidates = [
            i
            for i in range(len(lines) - 1)
            if lines[i].strip()
            and lines[i + 1].strip()
            and (len(lines[i]) - len(lines[i].lstrip())) == (len(lines[i + 1]) - len(lines[i + 1].lstrip()))
        ]
        if not candidates:
            return code
        i = rng.choice(candidates)
        lines[i], lines[i + 1] = lines[i + 1], lines[i]
        return "\n".join(lines)

    @staticmethod
    def _mutate_extend_append(code: str, rng: random.Random) -> str:
        if ".append(" in code and rng.random() < 0.5:
            return code.replace(".append(", ".extend(", 1)
        if ".extend(" in code:
            return code.replace(".extend(", ".append(", 1)
        return code

    _KEYWORDS = frozenset(
        {
            "False", "None", "True", "and", "as", "assert", "async", "await",
            "break", "class", "continue", "def", "del", "elif", "else",
            "except", "finally", "for", "from", "global", "if", "import",
            "in", "is", "lambda", "nonlocal", "not", "or", "pass", "raise",
            "return", "try", "while", "with", "yield", "self",
        }
    )

    @classmethod
    def _mutate_swap_identifier(cls, code: str, rng: random.Random) -> str:
        """Swap one identifier token for another in-scope identifier.

        Catches bugs like ``return value`` where ``return low`` was meant --
        a single wrong-name-returned mistake that comparison/constant
        mutations cannot reach. Python keywords are excluded so this never
        turns a name into ``return`` or ``if``.
        """
        occurrences = [
            m for m in _IDENTIFIER_RE.finditer(code) if m.group(0) not in cls._KEYWORDS
        ]
        names = sorted({m.group(0) for m in occurrences})
        if len(names) < 2 or not occurrences:
            return code
        target = rng.choice(occurrences)
        replacement = rng.choice([n for n in names if n != target.group(0)] or [target.group(0)])
        return code[: target.start()] + replacement + code[target.end():]

    @staticmethod
    def _mutate_duplicate_line(code: str, rng: random.Random) -> str:
        """Duplicate an earlier statement, re-indented, before the last line.

        Targets the classic "forgot to flush the accumulator before the
        final return" bug shape (e.g. run-length encoding), where the fix is
        literally repeating an earlier statement -- at the *return*
        statement's indentation -- just above it.
        """
        lines = code.split("\n")
        non_blank = [i for i, line in enumerate(lines) if line.strip()]
        if len(non_blank) < 2:
            return code
        last = non_blank[-1]
        last_indent = lines[last][: len(lines[last]) - len(lines[last].lstrip())]
        candidates = [i for i in non_blank[:-1] if i < last]
        if not candidates:
            return code
        source_line = rng.choice(candidates)
        reindented = last_indent + lines[source_line].strip()
        new_lines = lines[:last] + [reindented] + lines[last:]
        return "\n".join(new_lines)

    def mutate(self, code: str, attempts: int = 6) -> str:
        """Apply a small random mutation, retrying until the result compiles."""
        operators = [
            self._mutate_comparison,
            self._mutate_constant,
            self._mutate_swap_lines,
            self._mutate_extend_append,
            self._mutate_swap_identifier,
            self._mutate_duplicate_line,
        ]
        for _ in range(attempts):
            operator = self.rng.choice(operators)
            mutant = operator(code, self.rng)
            if mutant != code and World.compiles(mutant):
                return mutant
        return code

    def crossover(self, code_a: str, code_b: str) -> str:
        """Line-swap crossover between two same-length-ish candidates."""
        lines_a = code_a.split("\n")
        lines_b = code_b.split("\n")
        if len(lines_a) < 2 or len(lines_b) < 2:
            return code_a
        cut = self.rng.randint(1, min(len(lines_a), len(lines_b)) - 1)
        child = lines_a[:cut] + lines_b[cut:]
        candidate = "\n".join(child)
        return candidate if World.compiles(candidate) else code_a
