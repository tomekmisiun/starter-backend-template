# AGENTS.md

Project AI rules live in `.ai-rules/`. Read the relevant files before making
changes. Do not duplicate rule bodies here.

## Rule Index

- `.ai-rules/repository.md` — scope, config hygiene, enforcement split
- `.ai-rules/architecture.md` — layers, dependencies
- `.ai-rules/api.md` — routes, auth, versioning
- `.ai-rules/database.md` — SQLAlchemy, Alembic, destructive migrations
- `.ai-rules/security.md` — secrets, auth, production validators
- `.ai-rules/tenancy.md` — tenant isolation
- `.ai-rules/workers.md` — job queue and Redis compatibility
- `.ai-rules/testing.md` — pytest requirements and test integrity
- `.ai-rules/docker.md` — Compose and production runtime safety
- `.ai-rules/documentation.md` — README, docs, tracking files
- `.ai-rules/git.md` — branches, commits, push/merge approval

Mechanical checks: `docs/ci-policy-guards.md`.

Update `.ai-rules/` when changing project rules. Keep this file as an index only.
