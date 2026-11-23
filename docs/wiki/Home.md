# IXPANSION Open-Source Handbook

Welcome to IXPANSION: a modular engineering workspace for experiments, reusable skills, agent systems, simulation, and evidence-driven software.

## Start here

- [Architecture and system boundaries](architecture.md)
- [Codespaces and development container](codespaces.md)
- [OpenAI Platform integration](openai-platform.md)
- [Labs and experiment lifecycle](../../labs/README.md)
- [Contribution guide](../../CONTRIBUTING.md)
- [Security policy](../../SECURITY.md)
- [Repository README](../../README.md)

## Repository map

| Area | Purpose |
| --- | --- |
| `.devcontainer/` | Reproducible Codespaces and development-container setup |
| `docs/` | Reviewable technical documentation and handbook |
| `labs/` | Experiments, test chambers, prototypes, and results |
| `skills/` | Versioned reusable agent and engineering workflows |
| `tests/` | Automated regression and contract tests |
| `api/` | Service and integration surfaces |

## Evidence language

Every claim about behavior must identify its evidence:

- **VERIFIED**: reproduced by an identified test, run, or inspection.
- **SIMULATED**: exercised only in a simulated or mocked environment.
- **DEGRADED**: partially working, with a known limitation.
- **PENDING**: not yet verified.
- **CONTRADICTED**: evidence conflicts with the claim.

A passing unit test is not a production deployment. A screenshot is not a benchmark. Keep the evidence attached to the claim.

## Contribution path

1. Open an issue or document the hypothesis.
2. Create a focused feature branch.
3. Add tests and reproducible instructions.
4. Run the narrowest relevant checks, then the broader suite.
5. Open a pull request with scope, evidence, risks, and rollback notes.
6. Merge only after review and required checks.

The GitHub Wiki is the reader-friendly guide surface. The `docs/wiki/` files in this repository are the reviewable, version-controlled source. Keep them aligned through pull requests.
