# Repository Rules

## Scope

- Documentation-only or AI-rules-only tasks MUST NOT modify files under `app/`,
  `tests/`, `alembic/versions/`, or `.github/workflows/` unless the task
  explicitly requires it.
- MUST NOT make unrelated drive-by refactors when implementing a scoped task.

## Configuration

- Use `.env` for local secrets. MUST NOT commit `.env`.
- Keep `.env.example` limited to safe placeholders.
- MUST NOT hardcode secrets in code, Docker files, or docs.

## Enforcement vs Policy

- Mechanical checks (coverage floor, lockfile pairing, migration guards, secrets
  scans) live in CI, pre-commit, and `docs/ci-policy-guards.md`.
- `.ai-rules/` keeps judgment rules that automation cannot enforce.

## Source Of Truth For AI Rules

- `.ai-rules/` is the only source of truth for AI/project rules.
- `AGENTS.md`, `CLAUDE.md`, and `.cursor/rules/*.mdc` MUST only point to
  `.ai-rules/`.
- MUST NOT duplicate rule bodies in tool-specific wrapper files.
