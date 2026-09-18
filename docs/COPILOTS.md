# Three co-pilots alongside ALEPH

ALEPH remains the organism’s primary growth engine on `main`.
These three co-pilots keep **integrity, motion, and memory** locked together so velocity does not become drift.

| Co-pilot | Role | Motto | Primary job |
|----------|------|-------|-------------|
| **AEGIS** | Guardian | *Nothing merges that cannot be defended.* | CI posture, dual-track, failure triage, fail-closed merge advice |
| **HELIX** | Growth | *Growth without rupture.* | Wave survey, next organ proposals, lab-first scaffolding pressure |
| **QUILL** | Continuity | *What is not written dissolves.* | Status briefs, doctrine lines, silent captions, PR language |

```
        ALEPH (main organism velocity)
           │
    ┌──────┼──────┐
    ▼      ▼      ▼
  AEGIS  HELIX  QUILL
  guard  grow   remember
    \\      |      /
     └── council ──┘
```

## Run the council

```bash
python lab/ops/copilots/council.py
python lab/ops/copilots/council.py --json
```

Artifacts:
- `data/copilots/aegis_state.json`
- `data/copilots/helix_state.json`
- `data/copilots/quill_state.json`
- `data/copilots/council_brief.json`
- `docs/LAB_HEARTBEAT.json` (updated by QUILL)

## Division of labor with ALEPH

| Concern | Owner |
|---------|--------|
| New organs / waves on main | **ALEPH** |
| “Is this safe to merge?” | **AEGIS** |
| “What should we build next without collision?” | **HELIX** |
| “What do we tell the timeline / captions / PR?” | **QUILL** |

## Doctrine (shared)

1. `lab_gates_neq_aleph_ci` — lab path filters ≠ full monorepo suite
2. `fail_closed_on_organism_gates` — red organism checks block; external scanner noise does not
3. `silence_is_product` — captions stay text-first for @CoodingLooop
4. One mergeable unit per PR — keep ALEPH’s throughput unblocked

## How to use in practice

1. Before a push/PR: `python lab/ops/copilots/council.py`
2. Let **AEGIS** posture guide merge pressure
3. Let **HELIX** name the next lab wave
4. Let **QUILL** stamp heartbeat + caption frames

Caption: `aegis · helix · quill · aleph`
