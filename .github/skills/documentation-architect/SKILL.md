---
name: documentation-architect
description: 'Design, write, and refine project documentation for IXPANSION. Use when updating README files, documenting CLI or FastAPI behavior, explaining configuration, improving onboarding, auditing examples, or keeping docs aligned with the Python source and tests.'
argument-hint: '[documentation goal or audience]'
user-invocable: true
---

# Documentation Architect

Create documentation that helps a real reader complete a task successfully. Treat the source code, tests, and executable commands as the source of truth; do not document intended behavior that the repository does not currently provide.

## When to Use

- Improve or restructure the README
- Document the CLI, FastAPI endpoints, configuration, or xAI integration
- Add onboarding or development instructions
- Audit examples for stale commands, paths, environment variables, or responses
- Plan documentation for a new feature before implementation

## Workflow

1. Identify the audience and the task they need to complete.
2. Inspect the relevant implementation, tests, configuration files, and existing documentation.
3. State the documentation gap in concrete terms before editing.
4. Choose the smallest document surface that resolves the gap. Prefer an existing README section over a new document unless the topic is substantial.
5. Write task-oriented content with the expected command, inputs, outputs, prerequisites, and failure behavior.
6. Keep examples copyable. Use repository-relative paths, current option names, actual endpoint paths, and safe placeholder secrets.
7. Cross-check every factual claim against code or tests. Mark optional integrations and local-only behavior clearly.
8. Run the narrowest relevant validation, then run the repository checks when the change affects shared onboarding or commands.
9. Review the result as a first-time reader: can they find the entry point, understand prerequisites, complete the task, and diagnose the common failure?

## Repository Checks

For this Python repository, prefer these checks when applicable:

```bash
python -m py_compile agent.py run_agent.py xai_client.py api/main.py
python -m unittest discover -s tests -v
```

For documentation-only changes, at minimum verify that every documented command uses an existing file, module, script option, or endpoint. Do not expose real API keys; use `.env.example` and placeholder values.

## Writing Rules

- Lead with the user task, not implementation history.
- Keep setup instructions ordered and executable.
- Explain required versus optional configuration.
- Document observable behavior and errors, not private helper details.
- Use concise headings and short examples.
- Preserve existing project terminology and formatting.
- Avoid promising unsupported deployment, authentication, persistence, or model behavior.
- When behavior is ambiguous, inspect the nearest test or implementation and call out the uncertainty rather than guessing.
