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


## Frame Rate & Frame Creation Lab

The renderer UI includes an instrumented frame lab:

- Live render FPS, 1% low, frame index, simulation tick, and dropped simulation time and missed render-target counts.
- Render caps at 30, 60, 90, 120 FPS, or uncapped.
- Pause/resume and deterministic single-step controls.
- Bounded frame capture timeline (60 captures by default), thumbnail previews, duplicate, restore, JPG export, and JSON export.
- Rendering cadence is measured independently from the fixed 120 Hz physics step.
- Large frame gaps and excessive catch-up work are bounded and counted as dropped simulation time.

Frame captures contain a versioned physics snapshot, a bounded JPEG thumbnail, capture timestamp, frame index, simulation tick, and state hash. The hash is an equality aid, not a cryptographic proof. FPS values are device/browser measurements, not guaranteed output rates.

Run the frame lab and physics tests:

```sh
node --test holodeck/3d/frame-lab.test.mjs
node --test holodeck/physics.test.mjs
npm install --no-save --no-package-lock playwright
npx playwright install --with-deps chromium
node tests/holodeck-frame-lab.browser.mjs
```

The browser smoke checks WebGL initialization, live rendered FPS, pause/resume, single-step, frame capture/duplicate/restore, JPG and JSON downloads, and mobile layout. It runs in headless Chromium with SwiftShader; this is a CI smoke test, not a substitute for measuring physical device refresh rates.
