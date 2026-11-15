---
name: kitebridge-browser-federation
description: Route public-page browser capture through Cloudflare Kitesurf with strict target policy, bounded evidence, and Chromium fallback boundaries.
---

# KITEBRIDGE Browser Federation Skill

## Capabilities
- kitebridge:classify_task — select Kitesurf or Chromium based on task requirements
- kitebridge:capture_public_page — capture allowlisted public pages with Kitesurf
- kitebridge:verify_evidence — validate local evidence hashes without overstating source trust
- kitebridge:benchmark_route — compare compatible public tasks against Chromium

## Roots

| Root | Path | Responsibility |
|---|---|---|
| integration | integrations/kitebridge/ | Provider implementation and routing primitives |
| tests | tests/test_kitebridge_kitesurf.py | Fake-transport safety and contract tests |
| docs | docs/kitebridge-browser-federation.md | Architecture, configuration and activation gates |

## Routing rules

Use Kitesurf only for one-shot public-page tasks whose exact hostname is allowlisted. Route authenticated, persistent, WebGL/video, or bot-challenge tasks to Chromium. Never pass user cookies, passwords, authorization headers, or provider credentials to a page. Do not expose an unauthenticated self-hosted Kitesurf endpoint.

### kitebridge:classify_task

~~~python
if task.is_authenticated or task.requires_persistent_session or task.requires_webgl_or_video:
    route = "chromium"
elif task.is_public and task.hostname in exact_allowlist:
    route = "kitesurf"
else:
    route = "deny"
~~~

### kitebridge:capture_public_page

~~~python
adapter = KitesurfBrowserAdapter()
evidence = adapter.capture("https://docs.example.com/guide", task_id="docs-check-001")
# Evidence is LIVE/PENDING; hashes are integrity checks, not source verification.
~~~

### kitebridge:verify_evidence

~~~python
assert KitesurfBrowserAdapter.verify_evidence(evidence)
# Never upgrade PENDING to VERIFIED based on hashes alone.
~~~

### kitebridge:benchmark_route

~~~text
Use the same public URL/task corpus on Kitesurf and Chromium.
Record compatibility, wall time, CPU, memory, output bytes, extraction accuracy,
and failure rate. Keep authenticated and challenge pages out of the Kitesurf corpus.
~~~
