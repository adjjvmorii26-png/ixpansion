# Lab Refinements — OS Boot era

## Shipped (bigger than jumpstart)

| Artifact | Leap |
|----------|------|
| `subprocess_vitals.py` | True process isolation for dirty modules (190–197 class) |
| Pulse engine `workers` + `isolate_dirty` | Parallel cold pulse + subprocess for watchlist |
| `lab_os_boot.py` | Jumpstart + parallel pulse + dual-track + momentum → **BOOT_MANIFEST** |
| Wave **706** | Agent `boot` action |
| `lab-os-boot.yml` | Path-filtered CI (not ALEPH full suite) |

## Next refinements

| # | Item | Impact |
|---|------|--------|
| 1 | **Merge #122→#124 then OS boot PR** | Unlocks still/seal/jumpstart/os-boot on main |
| 2 | **conftest: call wave702 purge** after data reset | Closes remaining import pollution |
| 3 | **Lab smoke fail rule** | Fail only if BOOT_MANIFEST ok=false OR (changed && critical vitals fail) |
| 4 | **Dashboard OS strip** | Render fingerprint + layers_ok + ms from manifest |
| 5 | **Dirty list from config** | Move DIRTY_SUBSTRINGS to `lab/ops/dirty_modules.json` |
| 6 | **Process pool for isolate** | Reuse workers instead of one subprocess per dirty module |
| 7 | **Caption auto-deposit** | On boot changed=true, write silent caption frame for @CoodingLooop |

## Caption

`os boot · isolate · parallel · manifest`
