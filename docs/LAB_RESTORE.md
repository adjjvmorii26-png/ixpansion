# Lab branch restore · 2026-09-12

Branch `lab/chrono-forge-wave` recreated from main + organism lab overlay.

```bash
python lab/smoke_lab.py
python lab/ops/pr_graft_advisor.py
python apps/seamwalk/build_seams.py
```

Gates: Lab Smoke / Lab Graft path-filtered CI. Full monorepo CI is a separate track.
