---
name: reusable-ui-workbench
description: Create, inspect, edit, version, test, and reuse portable UI components and patterns across projects without duplicating brittle markup. Use when building design systems, component libraries, dashboard widgets, reusable HTML/CSS/JS, React components, or shared interface patterns.
---

# Reusable UI Workbench

## Mission
Treat every useful interface as a reusable asset, not a one-off pile of markup. Build a small, searchable component system that can be edited safely, previewed in isolation, reused across pages, and migrated between projects.

## Operating contract
- Inspect the existing repository, framework, package manager, design tokens, component conventions, and tests before editing.
- Prefer extending existing components over introducing near-duplicates.
- Work on a feature branch unless explicitly instructed otherwise. Never merge or push to the default branch as an assumed step.
- Keep edits scoped. Preserve public props, exports, accessibility behavior, and existing styling contracts unless the task explicitly changes them.
- Do not claim tests, previews, builds, deployments, or accessibility checks passed unless actually executed and observed.
- Avoid adding dependencies for problems solvable with existing tools.
- Ask before destructive migrations, broad renames, dependency upgrades, or breaking API changes.

## Workflow: COMPONENT → CONTRACT → EDIT → VERIFY → CATALOG

### 1. Discover
1. Identify the stack and entry points.
2. Search for an existing component, style token, utility, or pattern that already solves the problem.
3. Check current git status and recent history; do not overwrite unrelated changes.
4. Record the component's consumers and any existing test or story files.

### 2. Define the reusable contract
For each component, document:
- stable name and purpose
- framework/runtime and file locations
- public props/inputs, defaults, events/callbacks, and output
- variants and states (default, loading, empty, error, disabled, focus, hover)
- design tokens and responsive behavior
- accessibility expectations (semantic structure, keyboard use, labels, contrast)
- dependencies and known limitations
- usage example and test command

Prefer composition and explicit variants over boolean-prop explosions. Keep content separate from presentation when practical.

### 3. Edit safely
- Make the smallest coherent change.
- Keep component logic, visual tokens, and content separate where the stack supports it.
- Use semantic HTML and native controls before custom interaction.
- Make interactive elements keyboard-operable, visibly focused, and appropriately named.
- Include loading, empty, error, and disabled states when relevant.
- Avoid global CSS leakage. Scope styles or use the repository's established styling approach.
- Do not hard-code environment secrets, user data, or project-specific URLs into portable components.
- Keep a component's dependencies explicit; do not silently rely on unrelated page globals.
- Preserve mobile layouts, reduced-motion preferences, and zoom/reflow behavior.

### 4. Verify
Run the narrowest relevant checks first, then broader checks when practical:
1. existing component/unit tests
2. typecheck and lint for touched files
3. build or framework validation
4. visual/browser preview at narrow and wide viewports, if available
5. accessibility checks for labels, semantics, focus, keyboard interaction, and contrast

Report each check as **PASS**, **FAIL**, **NOT RUN**, or **BLOCKED**, with the exact command and concise evidence. Do not turn missing tooling into a pass.

### 5. Package for reuse
- Export through the repository's established public entry point when one exists.
- Add a minimal example showing the normal case and at least one meaningful variant.
- Add/update tests for behavior and important states.
- Update the component catalog or docs with props, dependencies, accessibility notes, and usage.
- Prefer semantic versioning for independently published packages; otherwise note breaking changes in the change summary.
- Avoid copying a component into another app if a shared package or source-of-truth import is already available.

## Editing an existing component
Before changing it, identify its consumers and current API. Preserve backward compatibility by default. If a breaking change is unavoidable, document the migration and update every in-repository consumer in the same change. Add a regression test for the reported defect.

## Reuse across projects
1. Confirm framework/runtime compatibility and licensing for copied or imported code.
2. Port tokens and public props, not hidden app-specific assumptions.
3. Replace hard-coded colors, spacing, URLs, and text with existing project tokens/config where possible.
4. Keep a provenance note linking to the original component or commit.
5. Run the receiving project's tests; a component passing in its source project is not proof it works in the target project.

## Output format
Summarize:
- what component(s) were created or edited
- files changed
- public API and usage example
- tests/build/preview actually run and their results
- known gaps or follow-up risks
- branch/commit/PR status, distinguishing created from merged

## Definition of done
A component is reusable when it has a clear contract, no accidental page-global dependencies, scoped styling, accessible states, a usage example, and at least one relevant verification path. A file merely moved into a folder does not qualify.