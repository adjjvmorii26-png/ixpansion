# IXPANSION monorepo hygiene (2026-11)

## CI truth model

1. **Empty-job / zero-duration failures on `main`**  
   Runs that complete with `jobs: 0` and no step logs are **not** suite failures.  
   Community reports match a synthetic `BuildFailed` / `startup_failure` platform pattern (GitHub Actions dispatcher), not application YAML.  
   Check: Settings → Actions enabled; billing budget not exhausted; then GitHub Support if persistent.

2. **App-level red (when jobs *do* run)**  
   Known fixed gap: Wave 103 CORS tests vs hardened allowlist middleware.  
   Branch: `fix/cors-tests-main-nov2026` — align tests, do not weaken CORS policy.

3. **Ubuntu runner pin**  
   `ubuntu-latest` is migrating to 26.04 (2026-10-19 → ~2026-11-19).  
   CI workflows pin `ubuntu-24.04` until suite is green on 26.04; then unpin deliberately.

## PR hygiene

Prefer **stacked PRs** (GA Oct 2026) for ordered landings:

1. CORS test alignment  
2. Workflow YAML / health CORS (#365)  
3. Manifold reactor live render (#373)  
4. Holodeck / Library drafts only after their own tests execute green

Do not merge drafts that explicitly say tests were not run.

## GitHub platform features to adopt (Universe / late 2026)

| Feature | Use for IXPANSION |
|---------|-------------------|
| **Stacked PRs** | Ordered CORS → CI → manifold stacks |
| **Actions workflow lockfiles** (`actions.lock`) | Pin third-party action SHAs; Dependabot updates lock + ref |
| **Workflow execution protections** | Restrict who/what can fire deploy-like workflows |
| **Agent Merge** ("Watch and fix" on PR) | Auto-fix Actions failures / conflicts when jobs run |
| **Agentic Workflows** | Issue triage + CI failure analysis in Actions |
| **Copilot Automations** | Label/triage stale drafts on schedule |
| **AI Scan for PRs** | Extra security pass on agent-heavy paths |

## Stale draft policy

Close or rebase drafts whose base is >40 commits behind `main` unless actively worked.  
Evidence claims require a run ID with non-zero jobs and step logs.
