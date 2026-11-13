# Get data storage off Vercel

## Storage layers

| Layer | Role | Authority |
|---|---|---|
| Upstash Redis or configured HTTPS JSON API | Durable source of truth | Authoritative |
| SquirrelCache (`api/squirrel_cache.py`) | Bounded SQLite TTL/LRU acceleration | Never authoritative |
| GitHub mirror | Cold archive only | Not a hot-path database |
| `/tmp` | Explicit ephemeral fallback | Not durable |

## SquirrelCache behavior

SquirrelCache is a local SQLite cache intended to reduce repeat reads from the
durable external store. It uses BEGIN IMMEDIATE transactions, WAL mode, TTL
expiry, entry and byte ceilings, and least-recently-used eviction.

It is opt-in per call:

```python
from api.off_vercel_store import get_json, set_json

# Read-through cache; remote durable store remains the authority.
state = get_json("telemetry/summary", {}, cache_ttl=15)
set_json("telemetry/summary", state, cache_ttl=15)
```

Cache configuration:
- `IXP_SQUIRREL_CACHE_PATH` (default `/tmp/ixp_squirrel_cache.sqlite3`)
- `IXP_SQUIRREL_CACHE_MAX_ENTRIES` (default `512`)
- `IXP_SQUIRREL_CACHE_MAX_BYTES` (default `8388608`)

Cache TTL is supplied by the caller. The default is zero, so caching is off
unless explicitly requested. Cache failures are non-fatal; durable backend
failures still raise `StoreError`. A cache hit is not proof of identity,
authorization, freshness beyond its TTL, or data integrity. Do not use this
cache as the sole source for API-key validation, authorization decisions,
billing counters, or transactional state.

On Vercel, SQLite cache files are local to a function instance and ephemeral.
They are not shared across instances and are not a replacement for Upstash.

## Durable backend

The runtime adapter prefers:
- `UPSTASH_REDIS_REST_URL` + `UPSTASH_REDIS_REST_TOKEN`, or
- `IXP_STATE_HTTP_GET` + `IXP_STATE_HTTP_PUT`.

The two variables for each backend must be configured together. Configured
backend failures raise errors rather than silently falling back to `/tmp`.

GitHub remains cold-archive only. Hot writes remain disabled unless
`IXP_ALLOW_GITHUB_HOT_WRITE=1` is explicitly enabled.

## Reduce deployment weight

`.vercelignore` excludes `data/**`, tests, docs, and artifacts from CLI deploy
uploads. Confirm the actual deployment method and artifact contents before
assuming this also changes Git-connected deployment behavior.

Do not create Vercel Blob, KV, or Postgres when the requirement is storage
outside Vercel. Do not remove historical `data/**` files until an archive and
restore verification exist.
