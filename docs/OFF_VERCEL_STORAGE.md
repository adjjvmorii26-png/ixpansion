# Get data storage off Vercel

## What was happening

1. **Ephemeral FS** — writes under the function filesystem die between invocations.
2. **GitHub mirror as “disk”** — `api/github_mirror.py` commits JSON into `data/`, which:
   - bloats the **git** history and **deployment** upload size
   - still feels like “Vercel storage” when every deploy ships `data/**`
3. **No Vercel Blob/KV** was connected on `ixpansion-live` (good — don’t add them if the goal is off-Vercel).

## What we shipped

| Change | Effect |
|--------|--------|
| `.vercelignore` | **Excludes `data/**`** (and tests/docs/artifacts) from the Vercel build upload |
| `api/off_vercel_store.py` | Runtime get/set prefers **Upstash Redis** or generic HTTP, not Vercel Blob |
| GitHub mirror | Keep for **cold archive only**; block hot writes unless `IXP_ALLOW_GITHUB_HOT_WRITE=1` |

## Recommended external store (free tier)

**Upstash Redis** (REST, works from serverless):

1. Create a Redis DB at upstash.com (not on Vercel storage).
2. Add to Vercel project env (production):
   - `UPSTASH_REDIS_REST_URL`
   - `UPSTASH_REDIS_REST_TOKEN`
3. In modules, prefer:

```python
from api.off_vercel_store import get_json, set_json
state = get_json("visitor_log", {"entries": []})
set_json("visitor_log", state)
```

## Reduce repo weight (optional but strong)

Large historical JSON under `data/` can move to a **separate private archive repo** or object storage (R2/S3/Backblaze). Keep only seed/manifest files in `ixpansion`.

```bash
# example: stop tracking a heavy file without deleting history yet
git rm --cached data/some_huge.json
# add to .gitignore: data/*.json (keep data/.gitkeep)
```

## Do not

- Create Vercel Blob / KV / Postgres if the goal is off Vercel storage
- Commit high-churn counters to `main` from production handlers
- Rely on `/tmp` for anything that must survive a cold start

## Verify

After merge + redeploy, deployment file size should drop (no `data/**` in the bundle). Runtime state goes to Upstash (or HTTP), not the deploy package.
