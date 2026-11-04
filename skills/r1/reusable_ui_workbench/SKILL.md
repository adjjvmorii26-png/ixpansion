---
name: reusable-ui-workbench
description: Create, inspect, edit, version, test, and reuse portable UI components, editable UI patterns, design tokens, and component libraries across projects. Use when building shared dashboards, design systems, UI kits, interactive previews, reusable HTML/CSS/JS, React components, or component migration workflows.
---

# Reusable UI Workbench

## Mission
Treat useful interfaces as durable, editable assets rather than one-off markup. Create a searchable source of truth that can be safely modified, previewed in isolation, versioned, tested, and reused across pages or projects.

## Capabilities
- `ui:discover` — inspect the project and locate existing components, tokens, consumers, and tests.
- `ui:contract` — define component API, variants, states, dependencies, and accessibility expectations.
- `ui:edit` — implement a focused, backward-compatible component change.
- `ui:compose` — build larger interfaces from existing components before creating new ones.
- `ui:preview` — prepare or use an isolated live preview when the project has a supported preview tool.
- `ui:verify` — run relevant tests, type checks, lint, build, and manual accessibility checks.
- `ui:catalog` — document the component and its provenance in the registry.
- `ui:extract` — extract repeated patterns into a shared component only when the repeated use cases genuinely share a contract.
- `ui:migrate` — port a component to another project while checking framework, token, dependency, and license compatibility.

These are workflow commands for an agent or developer, not guaranteed executable CLI commands. Do not claim a command ran unless an actual tool or script executed.

## Roots
| Root | Purpose |
|---|---|
| `skills/reusable-ui-workbench/` | Skill instructions, templates, and examples |
| `src/components/` | Example component location; discover the actual project structure before use |
| `src/styles/` | Example token/style location; discover the actual project structure before use |
| `tests/` or colocated tests | Test location; follow existing project conventions |

## Operating contract
- Inspect the repository, framework, package manager, design tokens, component conventions, test setup, and current git status before editing.
- Prefer extending an existing component over creating a near-duplicate.
- Work on a feature branch unless explicitly instructed otherwise. Never merge or push to the default branch as an assumed step.
- Preserve public props, exports, styling contracts, and accessibility behavior unless the task explicitly changes them.
- Keep changes scoped and do not overwrite unrelated user work.
- Do not claim tests, previews, builds, deployments, or accessibility checks passed unless actually executed and observed.
- Avoid adding dependencies when existing project tools can solve the problem.
- Ask before destructive migrations, broad renames, dependency upgrades, or breaking API changes.

## Workflow: DISCOVER → CONTRACT → COMPOSE/EDIT → PREVIEW → VERIFY → CATALOG

### 1. Discover
1. Identify the framework, runtime, build tool, styling method, package manager, and entry points.
2. Search for an existing component, token, utility, story, or pattern that solves the same problem.
3. Check git status and recent history; preserve unrelated changes.
4. Find component consumers, public exports, snapshots, stories, tests, and documentation.
5. Identify project constraints such as server/client boundaries, supported browsers, bundle budgets, and deployment platform.

### 2. Define the reusable contract
For each component, document:
- stable name, purpose, and intended use cases
- framework/runtime, source location, public export, and source of truth
- public props/inputs, types, defaults, events/callbacks, and output
- variants and states: default, hover, focus-visible, active, loading, empty, error, disabled, and success where relevant
- design tokens, theme behavior, responsive rules, and motion behavior
- accessibility expectations: semantic structure, accessible names, keyboard behavior, focus order, contrast, and reflow
- direct dependencies, provider/context requirements, environment assumptions, and known limitations
- minimal usage example, regression tests, and verification commands

Prefer composition and explicit variants over a large collection of interacting boolean props. Keep content separate from presentation when practical. Do not add states that do not make sense for the component.

### 3. Compose before duplicating
- Search for existing primitives and compose them to build larger patterns.
- Extract repeated markup only when the instances share the same meaning and behavior, not merely because their markup looks similar.
- Keep domain logic out of generic presentation components.
- Keep components small enough to understand and edit, but do not split every wrapper into a component without a reuse or clarity benefit.
- Preserve a clear owner and source of truth for shared components.

### 4. Edit safely
- Make the smallest coherent change that solves the stated need.
- Separate component logic, visual tokens, and content where the stack supports it.
- Use semantic HTML and native controls before custom interaction.
- Make interactive elements keyboard-operable, visibly focused, and appropriately named.
- Scope styles using the project's established method; avoid accidental global CSS leakage.
- Do not hard-code secrets, personal data, environment-specific URLs, or project-specific copy into portable components.
- Keep dependencies explicit; do not rely silently on unrelated page globals.
- Preserve mobile layouts, zoom/reflow behavior, reduced-motion preferences, and theme compatibility where applicable.
- For editable controls, define validation, save/cancel behavior, dirty-state handling, and error feedback. Do not imply changes are persisted if they only exist in local component state.

### 5. Preview and interactive editing
- Use the repository's existing storybook, dev server, test harness, or preview system when available; do not invent a preview URL.
- Preview components independently where possible, then check at least one real consuming page.
- Inspect narrow and wide viewports and the meaningful interactive states, not only the default screenshot.
- Separate design-time configuration from runtime user data.
- If live editing is supported, make changes reversible and provide reset/undo behavior where practical.
- Do not introduce an iframe, browser canvas, or new preview dependency unless it adds value and fits the existing architecture.
- Treat a successful deployment or preview build as evidence of deployability only, not proof of visual correctness or accessibility.

### 6. Verify
Run the narrowest relevant checks first, then broader checks as practical:
1. existing component/unit tests and regression tests
2. typecheck and lint for touched files
3. build or framework validation
4. visual preview at narrow and wide viewports, if available
5. keyboard, focus, semantic, accessible-name, contrast, reduced-motion, and zoom/reflow checks
6. integration check in a real consumer and destination project when portability is part of the task

Report each check as **PASS**, **FAIL**, **NOT RUN**, or **BLOCKED**, with the exact command or manual method and concise evidence. Distinguish automated results from manual inspection. Missing tooling is not a pass.

### 7. Catalog and version
- Export through the repository's established public entry point when one exists.
- Add a minimal example showing normal use and meaningful variants.
- Add/update tests for behavior and important states.
- Update the component registry with stable ID, source path, framework, API/docs references, dependencies, tests, accessibility notes, status, and provenance.
- Use registry statuses consistently: `draft`, `implemented`, `verified`, `deprecated`. A sample entry must be labeled `example`, not as a real verified component.
- Mark a component `verified` only when its documented checks have actually run.
- Prefer semantic versioning for independently published packages; otherwise document breaking changes and migration notes.
- Record origin repository/path/commit/license when copying or adapting code.

## Editing an existing component
Before changing it, identify its consumers and current API. Preserve backward compatibility by default. If a breaking change is unavoidable, explain why, document the migration, update every in-repository consumer, and add a regression test in the same change. Avoid silently renaming props or changing default behavior.

## Reuse across projects
1. Inspect the destination stack and compatibility constraints before choosing copy, package dependency, or source import.
2. Confirm license and provenance for external code.
3. Port public contracts and design tokens, not hidden app-specific assumptions.
4. Replace hard-coded colors, spacing, URLs, and copy with destination tokens/config where possible.
5. Check peer dependencies, runtime requirements, server/client boundaries, and bundle impact.
6. Run the destination project's own checks; source-project success does not prove destination compatibility.
7. If frameworks differ, adapt the behavior and contract deliberately rather than pretending the source component is directly portable.

## Example command workflows

### ui:discover
Inspect repository structure, git status, package metadata, matching components, and consumers. Report likely reuse candidates before creating files.

### ui:edit
Write a short change plan, edit the smallest set of files, preserve the public contract, and add a regression test for the changed behavior.

### ui:preview
Use an existing preview or dev workflow, state the exact command and URL only when observed, and inspect key states at narrow and wide viewport sizes.

### ui:verify
Run relevant tests, typecheck, lint, and build where available. Report each result individually; do not substitute a successful build for behavior tests.

### ui:catalog
Update the registry and component docs after implementation. Include API, variants, accessibility notes, tests, provenance, and the actual verification state.

### ui:migrate
Compare source and destination framework, tokens, dependencies, licensing, and exports; adapt, test, and document any incompatibility before declaring the component reusable.

## Output format
Summarize:
- components created or edited and the reason
- files changed and public API changes
- usage example or migration instructions
- tests/build/preview/accessibility checks actually run and results
- known gaps, assumptions, and follow-up risks
- branch, commit, PR, and merge status, clearly distinguishing each

## Definition of done
A reusable component has a clear contract, scoped styling, explicit dependencies, meaningful accessible states, a usage example, provenance when applicable, and at least one relevant verification path. Cross-project reuse also requires checks in the destination project. Moving a file into a folder alone does not make it reusable.
