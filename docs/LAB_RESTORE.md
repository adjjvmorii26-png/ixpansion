# Lab restore · Phases A+B complete (2026-09-12)

## Remote
- Branch: `lab/chrono-forge-wave`
- PR: https://github.com/adjjvmorii26-png/ixpansion/pull/106
- **Lab Smoke ✅ · Lab Graft ✅**

## Commands
```bash
python lab/smoke_lab.py
python lab/ops/phase_b_pipeline.py   # ticket → graft → seams → captions
python apps/seamwalk/serve.py        # http://127.0.0.1:8787/
```

## Next (Phase C)
- Weekly status includes lab branch alive Y/N
- Optional: land #106 when ready (organism gates already green)
