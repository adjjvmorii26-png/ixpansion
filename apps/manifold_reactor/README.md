# IXPANSION 5D Manifold Reactor

A standalone, local-only visual experiment. The renderer uses a small WebGL point shader with a Canvas 2D fallback; it does not load a third-party runtime or call external telemetry endpoints.

## Run

Serve the repository root with any static HTTP server, then open `/apps/manifold_reactor/`. ES modules may not work when opening the HTML as a `file://` URL.

Run the isolated core and experimental organism tests from the repository root:

```sh
node --test tests/manifold-reactor.test.mjs tests/experimental-organisms.test.mjs
```

## Experimental organisms

`experimental-organisms.mjs` contains framework-independent simulation primitives:
- `TemporalEchoRule` applies exponential residual-amplitude decay, creates immutable echo snapshots, and bounds cache capacity with expiry pruning and one refreshed entry per origin.
- `VacuumLeech` emits a capped drain request. It does not mutate world bandwidth; the host simulation remains responsible for validating and applying the request.

`TemporalEchoRule` is connected to an isolated Canvas 2D overlay. Echo evaluation runs only during fixed simulation steps; rendering reads immutable snapshots and does not mutate simulation state. The overlay remains independent of WebGL context loss and is cleared on simulation reset and page cleanup. `VacuumLeech` remains an unconnected action generator; no audio sonification or host-side bandwidth mutation is implemented.

## Hardening decisions

- Fixed-step simulation with capped frame time, capped catch-up steps, and explicit dropped-time accounting.
- Seeded PRNG; bounded particle count (1–1200) and energy level (0–2).
- WebGL shader compile/link checks, resource deletion, context-lost/restored handling, and low-power context hints.
- Pixel ratio capped at 1.75; animation stops while the tab is hidden; reduced-motion preference starts paused.
- Responsive controls with visible focus, labelled range/select inputs, 44px minimum button targets, status announcements, and a skip link.
- Audio is opt-in, low-volume, and closed during cleanup.
- No dynamic HTML injection, eval, external network requests, or remote scripts in the app.

## Evidence limits

The animation is illustrative. FPS and simulation ticks are local runtime counters, not authenticated telemetry or evidence about any external service. This app does not integrate the repository's EvidenceEnvelope or EvidenceVerifier, and no authenticity claim is made. No zero-allocation or 60 FPS performance claim is made for the experimental organism primitives.
