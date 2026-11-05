# Skill Lifecycle Control Plane

Notion is the canonical authoring and memory layer. IXPANSION is the versioned implementation and export layer. Gem-compatible folders are derived artifacts, not competing sources of truth.

## Standard pipeline

1. **Discover**: load enabled Notion skills; inspect existing skill and project context; search for duplicates.
2. **Seed**: author or refine the canonical Notion skill before downstream export.
3. **Genome scan**: compare source, export, tools, and runtime assumptions.
4. **Test**: use Rapid Test Loop for repository code; use Skill Genome & Mutation Lab for instruction behavior.
5. **Mutate**: one bounded change at a time, with baseline and rollback.
6. **Verify**: read back Notion and repository artifacts; run actual tests where execution is available.
7. **Export**: package only from the verified Notion source and preserve provenance.
8. **Promote**: PR review first. Merge, activation, sharing, and deployment remain separate approval gates.

## Canonical skills

- Notion Seed → Gem Skill Forge: https://app.notion.com/p/40f603736996816987e7e86f97e54172
- Skill Genome & Mutation Lab: https://app.notion.com/p/40f6037369968132bbafdfc4d4d0727b
- Rapid Test Loop seed: https://app.notion.com/p/40f603736996815da0f1ee7c5da70b77

## Evidence vocabulary

BUILT is not TESTED. DESK_TESTED is not EXECUTION_TESTED. A ready Vercel deployment is not PREVIEW_VERIFIED until opened and inspected. A PR being mergeable is not permission to merge.

## Project memory contract

Keep one canonical Notion hub for durable decisions, skill lineage, active PRs, known blockers, and next actions. Keep run logs and transient test output in separate records. Every status includes a source URL/ref and timestamp. Mark stale facts rather than silently carrying them forward.

## Guardrails

No fabricated tests, deployment claims, package archives, or tool capabilities. No production side effects, merges, destructive actions, or permission changes without explicit approval.
