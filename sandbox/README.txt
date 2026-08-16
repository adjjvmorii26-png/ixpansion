SANDBOX
=======

One organism, four organs, always evolving. This lives alongside IXPANSION
as a self-contained AI-agent code-generation playground: it writes, breaks,
tests, and repairs small Python programs forever, keeping every gain.

WHY IT EXISTS
-------------
IXPANSION is the operator/trust/safety scaffold. SANDBOX is the experiment
bench next to it: a place to let code mutate and get selected for fitness
under a real (but disposable) execution harness, with no external services
required. It is deliberately dependency-free (stdlib only) so it runs
anywhere IXPANSION runs, and it optionally reaches for an OpenAI-compatible
LLM (via the injected OPENAI_API_KEY / OPENAI_BASE_URL) when one is
available -- never as a requirement to stay alive.

THE FOUR ORGANS
----------------
world_builder.py
    Grows and reaps disposable "cells": fresh temp directories, a stripped
    environment (no inherited secrets), wall-clock timeout, and CPU/memory
    limits on POSIX. Runs candidate code against a generated test harness
    and reports a structured, JSON-scored ExecutionResult. This is the
    organism's body: it is where code actually lives and dies.

idea_lab.py
    The organism's diet and its genetic operators. Ships 8 built-in coding
    challenges (clamp, is_palindrome, flatten, most_common,
    run_length_encode, binary_search, merge_intervals, word_frequencies),
    each with a reference solution and a deliberately buggy seed, plus a
    generated harness. Also implements mutate() (comparison flips, constant
    nudges, adjacent same-indent line swaps, append/extend swaps) and
    crossover() (line-splice between two candidates), both syntax-gated so
    broken mutants are discarded before they ever run.

self_debugger.py
    The immune system. Given a failing cell, tries, in increasing order of
    cost: (1) pattern heuristics for common bug shapes (off-by-one
    comparisons, append/extend confusion, missing lowercasing, truthiness
    flips), (2) bounded evolutionary hill-climbing using idea_lab's
    mutate/crossover, keeping only strictly-better-or-simpler variants, and
    (3) optional LLM-assisted repair, used only if it compiles and actually
    improves measured fitness. Every judgment is behavioral: nothing here
    trusts static analysis, only harness re-runs inside a fresh world cell.

sandbox_engine.py
    The heartbeat. Each "tick": pick a challenge (favoring unsolved ones),
    load the organism's current best-known code for it (or the buggy seed on
    first contact), score it, heal it if broken, or spend a little effort
    simplifying it if it already passes. Every tick is appended to a
    persisted genome file at sandbox/state/genome.json (git-ignored, one
    organism per checkout) so progress accumulates across runs instead of
    resetting -- this is what makes it one continuously evolving organism
    instead of a disposable script.

RUNNING IT
----------
    cd sandbox
    python sandbox_engine.py --ticks 10
    python sandbox_engine.py --ticks 25 --use-llm
    python sandbox_engine.py --status

Or from the repository root:

    python -m unittest discover -s tests -v          # existing IXPANSION suite
    python -m unittest discover -s sandbox/tests -v  # sandbox organism's own tests

DESIGN NOTES
------------
- Offline-first: with zero configuration and zero network access, every
  challenge is still solvable through heuristics + evolution alone.
- Fail closed: the optional LLM bridge (llm_bridge.py) returns None on any
  error, missing key, or bad response -- callers always have a working
  offline fallback path, so a flaky endpoint can never stall the organism.
- No shared secrets reach a cell: world_builder strips the environment
  down to PATH/LANG-equivalents before ever exec'ing candidate code.
- Fitness is always re-measured, never cached across code changes: a
  candidate is only kept if a fresh harness run in a fresh cell says it is
  better (or equally correct and shorter).
- The genome file is intentionally plain JSON, not a database: it is meant
  to be read, diffed, and inspected by a human curious what the organism
  has learned.

EXTENDING IT
------------
Add a new Challenge to idea_lab._builtin_challenges() with a reference
solution, an intentionally buggy seed, and a harness built via the _harness()
helper. The engine and debugger need no changes -- they operate on any
Challenge with a `.buggy_seed`, `.harness`, and `.name`.
