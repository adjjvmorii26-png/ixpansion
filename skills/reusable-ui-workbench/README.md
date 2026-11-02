# Reusable UI Workbench

A framework-aware workflow for creating, editing, cataloging, verifying, and reusing UI components across IXPANSION and compatible projects.

## Quick start
1. Read [SKILL.md](SKILL.md).
2. Inspect the current component and its consumers before editing.
3. Copy [the component contract](templates/component-contract.md) for components intended for reuse.
4. Use [the registry example](examples/component-registry.json) as a lightweight catalog shape; replace the sample with real components before treating it as an inventory.
5. Run relevant repository checks and report actual results.

## Suggested component lifecycle
**Draft → Contracted → Implemented → Verified → Cataloged → Reused**

A component must not be labeled Verified unless its documented checks have actually run. Reuse should point to a source of truth or record provenance when copied.
