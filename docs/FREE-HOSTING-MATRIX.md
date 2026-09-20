# Free Hosting + Domain Matrix

Split deployment so the public dashboard does not depend on a paid Vercel plan.

## Recommended paths

| Surface | Provider | Free/default domain | Role |
|---|---|---|---|
| Dashboards | GitHub Pages | `adjjvmorii26-png.github.io/ixpansion` | Static HTML/CSS/JS |
| Dashboards | Cloudflare Pages | `<project>.pages.dev` | Static mirror / CDN |
| Python API | Google Cloud Run | `.run.app` | Python HTTP API |
| API/data/auth | Supabase | `.supabase.co` | Postgres, Auth, Storage |
| JS/TS edge | Cloudflare Workers | `.workers.dev` | Small edge APIs |
| Static fallback | Netlify | `.netlify.app` | Static + functions |

## Suggested topology

```
GitHub
  ├── GitHub Pages / Cloudflare Pages → dashboard/
  ├── Cloud Run → Python API
  └── GitHub Actions → build/test/deploy

Supabase → durable state (not local SQLite in containers)
```

## Domain plan (no paid domain required)

- Dashboard: `adjjvmorii26-png.github.io/ixpansion`
- API: Cloud Run hostname until a custom domain exists

## Boundary

Use the existing `deploy-pages.yml` workflow (`path: dashboard`). Do **not** upload the full monorepo root as a Pages artifact.

Organism gates > external GHAS-only noise for merge decisions.
