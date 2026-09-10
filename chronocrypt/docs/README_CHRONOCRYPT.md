# CHRONOCRYPT ORRERY

**Temporal mechanics & cyclic memory engine**

Chronocrypt Orrery treats time as a navigable, fracture-prone medium. Meridian streams carry linear flow, Gyres rotate cyclic periods, Fractures produce recoverable shards, and an Archive holds linear / cyclic / eroded vaults. A Choir of Cantors (Still, Turn, Break, Fade) maintains phase consensus across the orrery.

## Architecture

```
chronocrypt_orrery/
├── meridian/                  # Linear temporal streams
│   ├── streams/               # alpha, beta, gamma
│   ├── meridian_flow.js
│   ├── meridian_vector.tbl
│   └── meridian_pulse.hex
├── gyre/                      # Cyclic rotation engine
│   ├── cycles/
│   ├── gyre_rotation.js
│   ├── gyre_spiral.frag
│   └── gyre_period.tbl
├── fracture/                  # Break & suture domain
│   ├── shards/
│   ├── fracture_core.js
│   ├── fracture_entropy.hex
│   └── fracture_sutures.map
├── archive/                   # Multi-mode vaults
│   ├── vaults/
│   ├── archive_index.map
│   ├── archive_resonance.tbl
│   └── archive_echoes.stream
├── choir/                     # Cantor consensus
│   ├── agents/                # still, turn, break, fade
│   ├── choir_protocol.hex
│   ├── choir_voices.stream
│   └── choir_memory.echo
├── interfaces/
├── worlds/
│   ├── timeseeds/
│   └── collapsed/
├── docs/
├── chronocrypt.config
└── orrery_boot.sh
```

## Core Principles

1. **Time is multi-modal** — linear streams, cyclic gyres, and fractured shards coexist.
2. **Fracture is not loss** — shards remain suturable and archivable.
3. **Cantors keep phase** — four agents reach harmonic consensus each cycle.
4. **Archives remember modes** — linear, cyclic, and eroded vaults preserve different temporal signatures.
5. **Collapse leaves echoes** — recoverable traces for re-forging.

## Quick Start

```bash
chmod +x orrery_boot.sh
./orrery_boot.sh
```

Or:

```bash
node meridian/meridian_flow.js
node gyre/gyre_rotation.js
node fracture/fracture_core.js
```

## Lineage

Parallax → Astral Forge → Nebula Archive → Echotide Engine → **Chronocrypt Orrery**.
