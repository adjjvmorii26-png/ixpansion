# Workspace Architecture

## Authority boundaries

| System | Canonical responsibility | Must not become |
| --- | --- | --- |
| GitHub | Source code, issues, pull requests, releases, CI, security, versioned docs | A mirror of private secrets |
| GitHub Wiki | Reader-friendly project guides and onboarding | The only copy of critical technical specifications |
| Notion | Project registry, architecture decisions, skill index, experiment queue, audit pointers | A competing source of code truth |
| Google Drive | Research, datasets, generated artifacts, benchmark evidence, dated reports | A substitute for Git history |
| OpenAI Platform | API projects, model access, usage controls, key lifecycle | A place to publish API keys |
| IXPANSION Labs | Reproducible experiments and test environments | An unbounded production execution surface |

## Data flow

1. Code and documentation changes begin in GitHub branches.
2. CI produces machine-verifiable test and build evidence.
3. Notion records the project, decision, owner, status, and links to the exact commit and run.
4. Drive stores large artifacts and reports with the source commit SHA and evidence state.
5. OpenAI Platform projects provide scoped API access. Runtime credentials are injected through approved secret stores.

## Security boundaries

- Never commit API keys, tokens, private keys, or credential-bearing environment files.
- Never paste credentials into Notion or Drive.
- Use least-privilege project keys and rotate/revoke them through Platform controls.
- Keep untrusted experiment code isolated and resource-bounded.
- Require explicit approval before production writes, deployment, or irreversible operations.

## Change policy

Prefer small pull requests. Keep one concern per branch. Do not rewrite main history. Do not report a deployment as healthy based only on a successful build.
