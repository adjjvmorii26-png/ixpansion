# Wave 902 — Hypothesis Forge

Wave 902 is IXpansion's experimental proposal layer. It observes supplied
Wave 900/901 outputs and generates small, bounded hypotheses.

**Safety property:** proposals are data only. The module does not execute code,
perform external actions, mutate repositories, or claim that a hypothesis is true.

Each proposal contains a question, method, observation target, and falsifier.
The same inputs produce the same proposal set.
