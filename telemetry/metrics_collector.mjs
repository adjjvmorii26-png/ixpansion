/**
 * Vercel Metrics Collector — Wave 451 telemetry organ.
 *
 * Records runtime metrics via @vercel/functions' Metric API so they
 * surface in Vercel Observability:
 *
 *   import { metric } from '@vercel/functions';
 *   metric('query.duration_ms', 100, { plan: 'pro' });
 *
 * @vercel/node serverless function (Web-standard named method exports).
 * Paths:
 *   /vitals           -> record a duration metric
 *   /vitals?name=..   -> custom metric name + value + tag
 *   /vitals/health    -> liveness probe (also records a metric)
 */
import { metric } from '@vercel/functions';

const DEFAULT_TAGS = { plan: 'pro', organism: 'ixpansion' };

function json(body, status = 200) {
  return new Response(JSON.stringify(body, null, 2), {
    status,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      'cache-control': 'no-store, max-age=0',
      'access-control-allow-origin': '*',
    },
  });
}

function handle(request) {
  // Vercel runtime passes relative URLs — resolve against a safe base.
  const url = new URL(request.url, 'https://ixpansion.vercel.app');
  const path = url.pathname;

  if (path === '/vitals/health') {
    metric('vitals.health', 1, DEFAULT_TAGS);
    return json({ ok: true, organ: 'metrics_collector', wave: 451 });
  }

  const name = url.searchParams.get('name') || 'query.duration_ms';
  const rawValue = url.searchParams.get('value') || url.searchParams.get('ms') || '100';
  const value = Number(rawValue);
  const plan = url.searchParams.get('plan') || 'pro';
  const tag = url.searchParams.get('tag') || '';

  const tags = { plan, organism: 'ixpansion' };
  if (tag) tags.tag = tag;

  if (Number.isFinite(value)) {
    metric(name, value, tags);
  }

  return json({
    recorded: Number.isFinite(value),
    metric: name,
    value: Number.isFinite(value) ? value : null,
    tags,
    note: 'Visible in Vercel Observability → Metrics.',
  });
}

export function GET(request) {
  return handle(request);
}

export function POST(request) {
  return handle(request);
}
