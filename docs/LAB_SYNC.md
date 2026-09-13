# Lab Sync Policy

## Critical: Do Not Merge Stale Branches

**Never** merge `lab/chrono-forge-wave` wholesale into `main`.
The branch tip is divergent/stale and will:
- Delete CI workflows
- Trash CHANGELOG.md  
- Cause wave state conflicts

## Rebuild from Main (Recommended)

```bash
# 1. Start from clean main
git checkout main
git pull origin main

# 2. Apply additive sync only
# - docs/LAB_SYNC.md (this file)
# - lab/experiments/carnival.py
# - lab/ops/cf_bridge.py
```

## Local Stale Branch Cleanup

```bash
git fetch origin
git checkout lab/chrono-forge-wave
git reset --hard origin/main  # nuke stale history
# Now re-apply additive sync on top of clean main
```

## Dual Track Doctrine

| Track | Branch | Green Means |
|-------|--------|-------------|
| **Lab** | `lab/chrono-forge-wave` | Lab Smoke + Lab Graft |
| **ALEPH** | `main` | full `ci.yml` + wave deploys |

**Never confuse the tracks.** Two greens, one repo.

## Sync Commands

```bash
# Check lab smoke
python lab/ops/dual_track_card.py --smoke

# Check lab graft  
python lab/ops/dual_track_card.py --graft

# Chronoforge boot (always on main)
python lab/CHRONOFORGE/runtime/cf_portal.py boot
```
