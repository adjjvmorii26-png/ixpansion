# Wave 903 — Experiment Chamber

The Experiment Chamber is a deliberately narrow simulation layer. It accepts
declarative recipes and applies only four operations: add, remove, replace,
duplicate.

It records baseline/mutated digests and never performs external actions.
The goal is to make Wave 902 hypotheses testable without turning the
self-experimentation layer into arbitrary code execution.
