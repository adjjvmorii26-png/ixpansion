# Vercel Observability — Metric API + Speed Insights

The organism records runtime metrics into Vercel Observability through
the `@vercel/functions` Metric API, and captures client-side web vitals
through Vercel Speed Insights.

## Dependencies

- `@vercel/functions@3.9.5` — provides the `metric()` export
- `@vercel/speed-insights@^1.0.0` — client-side vitals

## Metric Recording Endpoint

```
GET /vitals?name=<metric>&value=<number>&plan=pro[&tag=<optional>]
```

Example:

```bash
curl "https://ixpansion-live.vercel.app/vitals?name=query.duration_ms&value=150&plan=pro"
```

The handler (`telemetry/metrics_collector.mjs`) calls:

```js
import { metric } from '@vercel/functions';
metric('query.duration_ms', 150, { plan: 'pro', organism: 'ixpansion' });
```

Metrics appear in the Vercel dashboard under Observability → Metrics.

## Health Probe

```
GET /vitals/health
```

Also emits `vitals.health = 1`.

## Promised Metrics

| Metric | Meaning |
|--------|---------|
| `query.duration_ms` | API request latency |
| `wave.growth` | evolution counter |
| `vitals.health` | liveness checks |
| `module.coherence` | coherence readings |
| `capybara.cycles` | protocol cycle completions |
| `silence.predictions` | silence oracle shifts |
| `error.crafts` | error-to-art creations |

The Python telemetry organ (`api/vercel_telemetry.py`) is exposed at
`/telemetry` with the full catalog and a recording log.

## Speed Insights

The client snippet is present in:

- `dashboard/index.html`
- `dashboard/vitals.html`
- `dashboard/ai_toolkit.html`
- `dashboard/wisdom_layer.html`
- `dashboard/capybara.html`

Speed Insights is enabled on the project (`/_vercel/speed-insights/script.js` → 200).
Captures TTFB, FCP, LCP, CLS, INP automatically.

## Compute + CDN

- Node 24 runtime for the metrics function (`@vercel/node`)
- Edge regions: `iad1`, `sin1`, `sfo1`
- CDN caching headers configured for dashboard assets
- Deployment is public (SSO protection disabled)

## Dashboards

- `/vitals-dash` — live Metric API + Speed Insights status
- `/telemetry` — Python telemetry catalog + recording log
- `/api/health` — organism health
