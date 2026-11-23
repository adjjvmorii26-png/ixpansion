# LOOPFORGE Builder Contracts

This directory defines stable interfaces for future media builders. It intentionally does not bind the project to one image/video model or paid provider.

## Builder interface

Every builder accepts a validated request and returns a plan plus provenance metadata. Provider calls, file writes, and publication are separate explicit operations.

- **MemeSeedBuilder**: deterministic prompt mutations from a premise and seed.
- **GifReactorBuilder**: frame timing, size budgets, seam analysis, and export plan.
- **ArtifactArchaeologist**: read-only inventory classification and duplicate review queue.

## Adapter boundary

Implementations should expose `validate(request)`, `plan(request)`, and `execute(plan, permissions)`. The execute stage must enforce least privilege, bounded resource use, and explicit confirmation for external writes. A builder must not silently publish or delete.

## Current implementation

The pure Python kernels in `loopforge/creative_kernels.py` implement the deterministic planning layer. They do not generate media or call AI providers. See `tests/test_loopforge_creative_kernels.py`.
