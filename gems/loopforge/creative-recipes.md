# LOOPFORGE Creative Gems

These are reusable recipes, not executable authorities. Each recipe produces a plan or draft; generation and publication remain separate actions.

## 1. Glitch-to-Giggle

**Input:** ordinary situation, one visual detail, optional reference asset.

1. State the situation in seven words or fewer.
2. Pick one mutation: scale inversion, expectation reversal, background punchline, or overconfident narrator.
3. Generate four caption directions from a fixed seed.
4. Keep the strongest caption under 120 characters.
5. Check legibility at mobile preview size.
6. Save the selected caption with seed and parent asset metadata.

**Variation knob:** absurdity 0–5. Increase one step at a time to avoid losing the premise.

## 2. Seamless Loop Alchemy

**Input:** frame sequence, target FPS, maximum duration.

1. Validate frame count and dimensions.
2. Build a bounded timing plan with `plan_gif`.
3. Compare first and last frame signatures with `loop_seam_score`.
4. If seam similarity is low, try a short crossfade or motion bridge as a separate derivative.
5. Compare playback at normal speed and at the loop boundary.
6. Export only after a human visual check; preserve the source sequence.

**Variation knob:** seam threshold. Treat 0.92 as a review prompt, not an objective guarantee of perceptual smoothness.

## 3. Museum of Almost-Forgotten Things

**Input:** repository or library inventory.

1. Collect references, compatibility, age, provenance, and duplicate candidates.
2. Run `assess_artifact` for each candidate.
3. Group results by status and show the evidence behind every label.
4. Surface likely reusable items before proposing replacements.
5. Archive only after explicit owner approval.
6. Record the source path and decision so an artifact can be restored.

**Variation knob:** stale threshold. Tune by artifact class; do not apply one age limit to everything.

## 4. Mutation Kaleidoscope

**Input:** one approved parent asset and a transformation brief.

1. Create three controlled variants that change only one dimension each.
2. Create one wild-card variant with a distinct seed.
3. Compare each variant against the parent for content drift and visual quality.
4. Keep parent and derivatives separately versioned.
5. Store a short note explaining what changed and why.

**Variation knob:** mutation distance low / medium / high. Always retain a low-distance fallback.
