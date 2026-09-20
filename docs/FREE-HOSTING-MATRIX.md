# Free Hosting + Domain Matrix

This repository can use a split deployment model so the public dashboard does not depend on a paid Vercel plan.

## Recommended paths

| Surface | Provider | Free/default domain | Role |
|---|---|---|---|
| Dashboards | GitHub Pages | `adjjvmorii26-png.github.io/ixpansion` | Static HTML/CSS/JS |
| Dashboards | Cloudflare Pages | `<project>.pages.dev` | Static mirror / CDN |
| Python API | Google Cloud Run | `<service>-<hash>.<region>.run.app` | Python HTTP API |
| API/data/auth | Supabase | `<project>.supabase.co` | Postgres, Auth, Storage, serverless data |
| JS/TS edge experiments | Cloudflare Workers | `<worker>.workers.dev` | Small edge APIs |
| JS/TS alternative | Deno Deploy | `<app>.deno.net` | Lightweight services |
| Static fallback | Netlify | `<site>.netlify.app` | Static + functions |

## Suggested topology

```
GitHub
  ├── GitHub Pages / Cloudflare Pages ──> dashboard
  ├── Cloud Run ────────────────────────> Python API
  └── GitHub Actions ──────────────────> build/test/deploy

Supabase
  ├── Postgres
  ├── Auth
  └── Storage
```

## Domain plan

No paid domain is required to start:

- Dashboard: `adjjvmorii26-png.github.io/ixpansion`
- Cloudflare mirror: `ixpansion.pages.dev`
- API: use the Cloud Run `.run.app` hostname

If a real domain is added later, keep the topology simple:

- `app.example.com` → dashboard
- `api.example.com` → Cloud Run API
- `docs.example.com` → documentation
- `lab.example.com` → experimental deployments

## Important boundary

The Python API should not rely on local SQLite/filesystem state for durable production data. Containers can be replaced. Put durable state in Postgres/object storage instead.

## Deployment notes

The GitHub Pages workflow in this branch is intentionally zero-secret. Cloudflare Pages and Cloud Run are documented as optional paths and require provider credentials/configuration before activation.
