# Repository Rules

Keep the repository clean, predictable, and easy to maintain.

## Project Structure

Expected backend structure:

- `app/main.py`
- `app/api`
- `app/core`
- `app/db`
- `app/models`
- `app/schemas`
- `app/services`
- `alembic`
- `tests`

## Maintainability

- Prefer simple, readable code.
- Use explicit names.
- Avoid premature abstractions.
- Avoid duplicated logic.
- Keep files focused on one responsibility.
- Keep changes small and reviewable.
- Preserve existing architecture unless the task explicitly requires changing
  it.
- Do not change application code when the task is limited to tooling,
  documentation, or AI rules.

## Configuration

- Use `.env` for local secrets and environment-specific values.
- Keep `.env` out of git.
- Keep `.env.example` safe and up to date.
- Do not hardcode secrets.

## Source Of Truth For AI Rules

- `.ai-rules` is the only source of truth for AI/project rules.
- Tool-specific files such as `.cursor/rules/*.mdc`, `AGENTS.md`, and
  `CLAUDE.md` must only point to `.ai-rules`.
- Do not duplicate rule bodies in tool-specific wrappers.
