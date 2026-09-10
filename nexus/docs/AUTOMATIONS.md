# Nexus Observatory — Automations

## Grok scheduled automations

| Name | Cadence | Purpose |
|------|---------|--------|
| **nexus-weekly-creative** | Weekly Mon 10:00 America/New_York | Creative lab briefing + next-wave proposal |

*(Additional Grok daily tasks may be blocked by task usage limits — use local scripts / Actions below.)*

## Local scripts (cron)

```bash
# Daily 09:00
0 9 * * *  /path/to/nexus_observatory/scripts/automate_daily.sh >> /tmp/nexus_daily.log 2>&1

# Weekly Monday 10:00
0 10 * * 1 /path/to/nexus_observatory/scripts/automate_weekly.sh >> /tmp/nexus_weekly.log 2>&1
```

| Script | Runs |
|--------|------|
| `scripts/automate_daily.sh` | seed → health → quiet → index → status |
| `scripts/automate_weekly.sh` | seed → creative → CI → prune → index → status |
| `scripts/automate_watch.sh [N] [ms]` | interval quiet cycles |

```bash
chmod +x scripts/*.sh
npm run auto:daily
npm run auto:weekly
npm run auto:watch
```

## GitHub Actions

`.github/workflows/nexus-ci.yml`

| Trigger | Jobs |
|---------|------|
| Push / PR `main` | Interop CI, wave9_pass, status artifact |
| Cron `0 13 * * *` UTC | CI + creative cycle |
| `workflow_dispatch` | Manual full run |
