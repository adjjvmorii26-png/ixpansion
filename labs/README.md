# IXPANSION Labs

A bounded playground for prototypes, performance studies, reusable test chambers, and agent experiments.

## Lifecycle

**Intake → Hypothesis → Sandbox → Test → Evidence → Review → Promote or Retire**

Every experiment must include:

- Problem and falsifiable hypothesis
- Scope and explicit non-goals
- Threat model and resource limits
- Environment and dependency versions
- Reproduction command
- Expected result and failure criteria
- Actual result, evidence links, and evidence classification
- Cleanup and rollback procedure

## Suggested lab zones

| Zone | Contents |
| --- | --- |
| `experiments/` | Time-bounded experiments and prototypes |
| `benchmarks/` | Repeated performance trials and raw results |
| `testbeds/` | Reusable simulation and browser test chambers |
| `fixtures/` | Sanitized test data and deterministic seeds |
| `templates/` | Experiment and benchmark templates |

## Reproducibility contract

- Pin dependencies where practical.
- Record OS, runtime, browser, hardware, and commit SHA.
- Use deterministic seeds for stochastic tests.
- Separate functional correctness from performance claims.
- Repeat performance trials and report distributions, not a single best run.
- Preserve raw output alongside summaries.
- Never describe headless results as physical-device validation.

## Safety rails

Labs are not production by default. Network access, filesystem writes, secrets, subprocesses, and resource consumption must be explicitly bounded. Experiments that require credentials use a secret store and a dedicated low-privilege project.
