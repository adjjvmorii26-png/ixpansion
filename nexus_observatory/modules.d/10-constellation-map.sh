#!/usr/bin/env bash
# Constellation map module — renders an ASCII sky chart of tracked objects.

module_boot() {
    cat <<'SKY'
    ┌─────────────────────────────────────────────┐
    │  ✦ Nexus Constellation Map                  │
    │                                             │
    │         ·  ·        ·                       │
    │      ·        ✦           ·                 │
    │          ·       ·    ✦                     │
    │    ·            ·           ·    ✦          │
    │         ✦        ·                          │
    │              ·         ·                    │
    │  tracked: 7 objects | drift: nominal        │
    └─────────────────────────────────────────────┘
SKY
}
