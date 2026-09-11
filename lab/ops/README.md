# Lab Ops · PR / CI / sandbox / codespace

| Tool | Innovation |
|------|------------|
| epoch_ticket.py | HMAC time-bound tickets; writes need `act` mode |
| pr_graft_advisor.py | PR as graft → hold/observe/act |
| sandbox_guarded.py | Ticks only with fresh ticket |
| codespace_boot.sh | postCreate = constellation + smoke + graft |
| lab-graft.yml | Path-filtered CI + graft artifact |

```bash
python lab/ops/epoch_ticket.py issue --ttl 3600
python lab/ops/sandbox_guarded.py 10
python lab/ops/pr_graft_advisor.py
bash lab/ops/codespace_boot.sh
```
