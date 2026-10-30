# Holodeck 3D Renderer v0.1

Spatial rendering layer for Holodeck Core.

## Scope

- Three.js scene (WebGL)
- Perspective camera + orbit-style drag
- Directional + ambient lighting
- Sphere meshes driven by Holodeck physics state
- Ground plane and simple materials

## Non-goals (this iteration)

- Not a photorealistic engine
- No WebGPU compute
- Physics remains in `holodeck/physics.mjs` (2D toy) or a future 3D integrator
- No AI agency yet

## Run

Open `holodeck/3d/index.html` via any static server (or GitHub/Vercel preview).

## Architecture

```
physics.mjs (or future 3d-physics)  →  state snapshot
                ↓
         renderer.mjs  →  Three.js scene graph
                ↓
           index.html  →  UI + rAF loop
```

Keep rendering and simulation separated so tests can stay headless.
