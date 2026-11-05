# Holodeck Core v0.1

A first, intentionally bounded prototype for IXPANSION's conversational spatial test-bed.

## Current scope
- Single-page canvas interface with a live particle/body sandbox.
- Fixed-step toy physics with configurable gravity and mass.
- Typed natural-language command patterns (no model/API required yet).
- Snapshot/restore, isolated timeline branches, and a state checksum.
- Bounded body count and parameter validation.

## Honest limitations
This version is a 2D canvas prototype, not photorealistic 3D, a molecular simulator, a validated fluid/structural solver, or an unbounded simulation. The FNV-1a state checksum detects state differences; it is not cryptographic proof or proof of physical correctness. Rendering rate depends on the device and browser. The AI, voice, gesture, WebGPU, and collaboration layers are not implemented.

## Run
Open `holodeck/index.html` in a modern browser. Tests require Node.js 18+:

```sh
node --test holodeck/physics.test.mjs
```

## First acceptance gates
1. Physics tests pass.
2. Snapshot restore and branch isolation remain deterministic.
3. Invalid inputs fail without mutating valid state.
4. Browser smoke test confirms canvas, controls, and command handling.
5. Record frame timing on target devices before making performance claims.
