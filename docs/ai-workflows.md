# AI Workflows

How AI tooling should use this repository's rules, personas, and commands.

## Layers

| Layer | Location | Binding? | Purpose |
|-------|----------|----------|---------|
| **Project rules** | `.ai-rules/` | **Yes** | Architecture, security, testing, git, docs — must follow |
| **Entry indexes** | `AGENTS.md`, `CLAUDE.md` | Pointer only | Tool-specific entry; no duplicated rule bodies |
| **Cursor wrappers** | `.cursor/rules/*.mdc` | Pointer only | Load `.ai-rules/` context in Cursor |
| **Workflow rules** | `.ai-rules/agent-orchestration.md`, etc. | **Yes** | How to start tasks, plan, review, onboard |
| **Personas** | `agents/` | Optional | Review lenses (backend, security, tenancy, …) |
| **Commands** | `.commands/` | Optional | Copy-paste prompts for spec/plan/review/onboard |
| **Specs** | `docs/specs/` | Optional | Larger feature specs before implementation |
| **ADRs** | `docs/adr/` | Reference | Recorded architecture decisions |

## Start every task

1. Read `.ai-rules/agent-orchestration.md`
2. Use `.ai-rules/context-map.md` to open relevant binding rules and code paths
3. For non-trivial work: `.ai-rules/spec-driven-development.md` →
   `.ai-rules/planning-and-task-breakdown.md` → `.ai-rules/incremental-work.md`
4. Before merge: `.ai-rules/review.md`

## Common commands (copy from `.commands/`)

| Goal | File |
|------|------|
| Write a spec | `.commands/spec.md` |
| Break into tasks | `.commands/plan.md` |
| Implement next roadmap item | `.commands/build-next-roadmap-task.md` |
| Pre-PR review | `.commands/review-current-branch.md` |
| Security audit | `.commands/security-audit.md` |
| Clone for new product | `.commands/template-onboard.md` |
| Sync tracking docs | `.commands/update-project-status.md` |

## Personas (review only)

| Persona | File |
|---------|------|
| Backend / FastAPI | `agents/backend-reviewer.md` |
| Security | `agents/security-auditor.md` |
| Tenancy | `agents/tenancy-reviewer.md` |
| Database / migrations | `agents/database-reviewer.md` |
| Docker / CI | `agents/devops-ci-reviewer.md` |
| Template clone | `agents/template-onboarding-agent.md` |

Personas **do not override** `.ai-rules/`. They add focus for review tasks.

## Validation

| Change | Command |
|--------|---------|
| App / tests / migrations | `make validate` |
| CI policy scripts | `make policy-guards` |
| AI workflow file presence | `make validate-ai-workflows` |

## Template reuse

Human docs: `docs/template-onboarding.md`, `docs/template-usage.md`,
`TEMPLATE_FREEZE_CHECKLIST.md`.

Agent workflow: `.ai-rules/template-onboarding.md` + `.commands/template-onboard.md`.

## Updating this stack

- New **binding** rule → `.ai-rules/<topic>.md` + index lines in `AGENTS.md` /
  `CLAUDE.md` / `.cursor/rules/project.mdc`
- New **workflow** → `.ai-rules/` + mention in `docs/ai-workflows.md`
- New **persona** → `agents/` + row in this file
- New **command prompt** → `.commands/` + row in this file
- Extend `scripts/validate-ai-workflows.sh` when adding required paths

Mechanical enforcement: `docs/ci-policy-guards.md`.
