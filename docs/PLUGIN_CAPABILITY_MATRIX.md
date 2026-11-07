# IXPANSION Plugin Capability Matrix

| Adapter | Reusable role | Exposed capabilities | Initial observed state |
|---|---|---|---|
| GitHub | Canonical code and CI | repositories, branches, commits, PRs, issues, workflow evidence | Connected; IXPANSION admin/push permission confirmed |
| GitLab | Secondary code and CI | projects, repositories, merge requests, pipelines, jobs | Connector exposed; connection not verified |
| Notion | Knowledge and skills index | search, pages, databases, skills, comments | Connected |
| Google Drive | Research and artifact storage | search, folders, files, metadata | Connected through Composio |
| Gmail | Correspondence and notifications | search, drafts, messages | Composio connection inactive; native Gmail tools exposed |
| Google Calendar | Scheduling | events, availability | Connector exposed; account write state not probed |
| Supabase | Application persistence | projects, tables, SQL, migrations, edge functions, advisors | Two projects visible; both report INACTIVE |
| Vercel | Runtime and deployment | projects, deployments, logs, sandboxes, environment metadata | Team and projects visible |
| Dropbox | Secondary artifact storage | search, files, folders, revisions, Paper | Connected |
| Canva | Visual artifacts | designs, templates, editing, generation | Connector exposed; account write state not verified |
| Figma | Product design | design context, variables, diagrams, code connect | Connected; View seat observed |
| OpenArt | Media generation | images, video, projects, assets | Connected; 40 credits observed at inspection |
| Website Maker | Website scaffolding | build brief handoff | Connector exposed |
| Plugin Creator | Custom plugin lifecycle | create, inspect, update, release | No owned personal plugins returned |
| Composio | Cross-app orchestration | tool discovery, multi-app execution, remote workbench, skill management | Connected; GitHub, Notion, Drive active |
| Files | Conversation/library artifacts | search, read, materialize, library management | Available |

## Adapter contract

Each adapter declares identity/version, connection state, read/write capabilities, permission names, idempotency, pagination, approval class, verification method, and evidence sink.

## State semantics

- `connected_verified`: an authenticated read-only probe succeeded.
- `connected_view_seat`: identity is connected but the observed seat is view-only.
- `connector_available_connection_unverified`: tools exist; account authorization has not been established.
- `connected_projects_inactive`: project metadata is visible, but projects are not ready for runtime writes.
- Recheck all states immediately before writes. This matrix is a dated observation, not a durable authorization grant.
