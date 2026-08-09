---
name: workflow-library
description: 'Select and run one of 80 bounded IXPANSION workflow recipes. Use when a task needs a repeatable path for planning, implementation, testing, operations, security, documentation, or release work.'
argument-hint: '[workflow name or desired outcome]'
user-invocable: true
---

# Workflow Library

Select the smallest recipe that matches the requested outcome. Every recipe
starts by stating the execution boundary, inspecting the owner, and ends with
focused validation plus an honest limitations report. Use `workflow-force` when
multiple recipes must be coordinated.

## Selection Protocol

1. Match the requested outcome to one recipe by its name and domain.
2. If several recipes match, choose the narrowest one that can produce evidence.
3. If the work crosses domains, select one primary recipe and list the others as supporting checks.
4. Use `workflow-force` when the work needs an ordered chain of three or more recipes.

## Execution Contract

For the selected recipe, record:

- **Boundary**: read-only, simulated, local, or externally effectful.
- **Owner**: implementation surface and relevant tests.
- **Evidence**: command, assertion, observation, or review finding.
- **Failure**: what was blocked, exhausted, unavailable, or left unverified.
- **Closeout**: changed files, validation result, limitations, and next decision.

## Planning And Discovery

1. **Clarify Mission**: intake -> acceptance criteria -> first discriminating check.
2. **Map Ownership**: nearest caller -> decision point -> owning module -> tests.
3. **Assess Impact**: callers -> contracts -> risks -> regression checks.
4. **Plan Vertical Slice**: inputs -> implementation -> boundary test -> report.
5. **Explore Unknown Code**: search -> read neighbor -> form hypothesis -> verify.
6. **Compare Alternatives**: constraints -> options -> tradeoffs -> selected path.
7. **Define Non-Goals**: requested behavior -> exclusions -> safety boundary -> sign-off.
8. **Resolve Ambiguity**: competing interpretations -> evidence -> decision -> record.
9. **Prepare Delegation**: scope -> file ownership -> agent role -> handoff evidence.
10. **Review Existing Pattern**: find analogue -> compare invariants -> reuse or justify change.

## Python Implementation

11. **Add Python Feature**: owner -> smallest edit -> focused test -> compile.
12. **Fix Regression**: reproduce -> identify root cause -> patch -> rerun reproduction.
13. **Refactor Safely**: callers -> behavior characterization -> small refactor -> tests.
14. **Add Configuration**: source of truth -> defaults -> validation -> offline test.
15. **Harden Parsing**: valid input -> malformed input -> explicit error -> boundary test.
16. **Add Domain Model**: invariants -> constructor -> serialization -> round-trip test.
17. **Add Service Boundary**: interface -> dependency injection -> fake implementation -> test.
18. **Add State Transition**: states -> allowed transitions -> invalid transition -> test.
19. **Add Idempotency**: stable identifier -> duplicate request -> same result -> test.
20. **Remove Dead Code**: usages -> tests -> deletion -> import and compile checks.

## API And CLI

21. **Add API Route**: contract -> implementation -> TestClient -> documentation.
22. **Change API Payload**: compatibility review -> schema -> success and error tests.
23. **Verify Health Check**: route -> status -> payload -> local smoke test.
24. **Update OpenAPI**: route behavior -> generated schema -> contract assertion.
25. **Add CLI Option**: parser -> default -> help -> valid and invalid tests.
26. **Fix CLI Exit Code**: reproduce -> expected code -> error path -> regression test.
27. **Improve CLI Error**: failure source -> safe message -> actionable hint -> test.
28. **Document Command**: inspect parser -> copyable example -> verify invocation.
29. **Test Offline CLI**: clear credentials -> deterministic path -> output assertion.
30. **API Failure Matrix**: malformed input -> unavailable dependency -> exact status checks.

## Testing And Verification

31. **Write Focused Test**: behavior -> fixture -> assertion -> smallest test run.
32. **Add Boundary Coverage**: input boundary -> owner -> failure mode -> test.
33. **Test Retry Exhaustion**: fake failure -> bounded attempts -> terminal result.
34. **Test Partial Failure**: successful units -> failed unit -> aggregate result -> audit.
35. **Test Replay**: stable task id -> duplicate execution -> idempotent assertion.
36. **Run Verification Ladder**: focused test -> compile -> suite -> diff check.
37. **Review Test Quality**: determinism -> isolation -> meaningful assertion -> cleanup.
38. **Test Security Gate**: unsafe input -> rejection -> no side effect -> audit assertion.
39. **Test Capacity Limit**: budget -> exhaustion -> bounded result -> diagnostic.
40. **Test Stale State**: stale fixture -> rejection or degrade -> observable result.

## Resilience And Operations

41. **Bound External Call**: timeout -> retry budget -> safe failure -> test.
42. **Design Degraded Mode**: missing dependency -> local fallback -> limitation report.
43. **Handle Capacity Loss**: unavailable node -> reallocation -> bounded outcome.
44. **Protect Queue**: enqueue limit -> overflow policy -> operator signal.
45. **Validate Lease**: acquire -> expiry -> invalid use -> rejection test.
46. **Recover Local Runtime**: reproduce -> inspect logs safely -> restart boundary -> smoke test.
47. **Run API Smoke Check**: start local server -> health route -> representative route -> stop.
48. **Run CLI Smoke Check**: command help -> offline command -> expected output -> exit code.
49. **Check Compose Config**: parse configuration -> inspect services -> report missing secrets.
50. **Prepare Incident Diagnosis**: symptom -> evidence -> containment -> next check.

## Trust And Safety

51. **Audit Secret Handling**: sources -> logs -> docs -> redaction findings.
52. **Review URL Allowlist**: input URL -> parser -> allowlist -> rejection test.
53. **Review Human Gate**: action classification -> approval boundary -> blocked path.
54. **Review Trust Update**: evidence -> bounded update -> namespace -> test.
55. **Review Quarantine**: trigger -> state change -> blocked execution -> recovery path.
56. **Review Audit Event**: decision -> fields -> redaction -> assertion.
57. **Review Dependency Risk**: declaration -> import -> optionality -> offline install path.
58. **Review Environment Loading**: precedence -> missing values -> safe defaults -> test.
59. **Review External Effect**: side effect -> authorization -> dry run -> confirmation gate.
60. **Prepare Security Regression**: threat -> reproduction -> fix -> negative test.

## Lattice And Federation

61. **Allocate Lattice Work**: request -> capacity -> lease -> result -> release.
62. **Test Lattice Exhaustion**: full capacity -> rejection or queue -> bounded response.
63. **Review CRDT Merge**: divergent states -> merge -> invariant -> replay test.
64. **Review Shard Boundary**: key -> owner shard -> routing -> unavailable shard.
65. **Review Federation Join**: identity -> trust -> capability -> admission result.
66. **Review Federation Retry**: stable operation -> transport failure -> replay -> result.
67. **Review Migration**: source state -> transfer -> destination validation -> cutover.
68. **Review Degraded Federation**: remote unavailable -> local operation -> limitation.
69. **Review Transport Contract**: simulated path -> real path -> distinct evidence.
70. **Run Local Federation Demo**: configure local nodes -> execute -> inspect state -> report.

## xAI And Integrations

71. **Verify xAI Configuration**: environment -> model -> endpoint -> safe missing-key behavior.
72. **Test xAI Request**: payload -> timeout -> response parse -> redacted failure.
73. **Test xAI Unavailable**: fake network failure -> offline fallback -> deterministic output.
74. **Review Token Routing**: request -> route selection -> budget -> result.
75. **Review Integration Adapter**: interface -> fake dependency -> contract test -> docs.
76. **Audit Integration Logs**: request metadata -> sensitive fields -> redaction -> test.

## Documentation And Release

77. **Update README**: source and tests -> task-oriented section -> command verification.
78. **Document Limitation**: observed capability -> unsupported claim -> explicit boundary.
79. **Prepare Release**: status -> tests -> contracts -> security -> version evidence.
80. **Review Change Set**: diff -> findings by severity -> validation -> residual risk.

## Completion Rules

- Keep network, credentials, destructive actions, and deployment behind explicit boundaries.
- Preserve public contracts unless the selected workflow explicitly includes a contract change.
- Never report simulated, process-local, or unauthenticated behavior as production-ready.
- Never commit, push, reset, create branches, or open pull requests unless explicitly requested.
