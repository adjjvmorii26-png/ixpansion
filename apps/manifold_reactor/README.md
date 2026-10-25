# IXPANSION 5D Manifold Reactor

A standalone, local-only visual experiment. The renderer uses a small WebGL point shader with a Canvas 2D fallback; it does not load a third-party runtime or call external telemetry endpoints.

## Run

Serve the repository root with any static HTTP server, then open `/apps/manifold_reactor/`. ES modules may not work when opening the HTML as a `file://` URL.

Run the isolated core tests from the repository root:

```sh
node --test tests/manifold-reactor.test.mjs
```

## Hardening decisions

- Fixed-step simulation with capped frame time, capped catch-up steps, and explicit dropped-time accounting.
- Seeded PRNG; bounded particle count (1–1200) and energy level (0–2).
- WebGL shader compile/link checks, resource deletion, context-lost/restored handling, and low-power context hints.
- Pixel ratio capped at 1.75; animation stops while the tab is hidden; reduced-motion preference starts paused.
- Responsive controls with visible focus, labelled range/select inputs, 44px minimum button targets, status announcements, and a skip link.
- Audio is opt-in, low-volume, and closed during cleanup.
- No dynamic HTML injection, eval, external network requests, or remote scripts in the app.

## Evidence limits

The animation is illustrative. FPS and simulation ticks are local runtime counters, not authenticated telemetry or evidence about any external service. This app does not integrate the repository's EvidenceEnvelope or EvidenceVerifier, and no authenticity claim is made.
