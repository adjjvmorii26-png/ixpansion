# Lab branch sync policy

## Situation (2026-09-13)

| Ref | SHA | Note |
|-----|-----|------|
| **main** | `7879dff` | CHRONOFORGE + full lab tree · ALEPH truth |
| **lab/chrono-forge-wave** | `86add52` | Exists on remote; **divergent/stale** vs main |
| **lab/rail-sync** | this branch | Rebuilt **from main** + additive experiments only |

### Do **not** merge old `lab/chrono-forge-wave` wholesale into main
Stale tip can show:
- CI workflow deletion (~92 lines) — **reject**
- Huge CHANGELOG/CITATION noise — review only
- api/ drift — prefer main's wave organs

### Do merge (additive)
- `lab/experiments/carnival.py` + floor shows
- `lab/evolve/fold_pressure.py` · `meaning_density` if missing
- `lab/experiments/mirror_well.py`
- Keep **CHRONOFORGE** on main as organism base:

```bash
python lab/CHRONOFORGE/runtime/cf_portal.py invariants
python lab/CHRONOFORGE/runtime/cf_portal.py transition-plan E2
python lab/CHRONOFORGE/runtime/cf_portal.py boot
```

### Local fix for stale branch
```bash
git fetch origin
git checkout lab/chrono-forge-wave
git reset --hard origin/main   # re-root on ALEPH
# cherry-pick only additive paths from lab/rail-sync if needed
```

Dual-track remains: experiment on lab rails · promote by **narrow** PR · never delete CI from a stale tip.
