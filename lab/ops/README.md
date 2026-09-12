# Lab Ops

| Tool | Role |
|------|------|
| epoch_ticket.py | HMAC TTL tickets |
| pr_graft_advisor.py | hold/observe/act |
| phase_b_pipeline.py | ticket → graft → seams → captions |
| lab_heartbeat.py | weekly-ready lab pulse |
| smoke_lab.py | required: helix + ops |

```bash
python lab/smoke_lab.py
python lab/ops/lab_heartbeat.py
python lab/ops/phase_b_pipeline.py
```
