# Testing Rules

Use pytest for backend tests.

## Requirements

- Add tests for new features.
- Add tests for every new endpoint.
- Add regression tests for bug fixes.
- Add tests for auth, permissions, session logic, migrations, Redis/rate limit
  behavior, and important business rules when touched.
- Do not break existing tests.
- If tests fail, fix the cause and rerun relevant tests.

## Before Commit

Run relevant validation before committing:

- `ruff check .`
- `pytest`
- `alembic upgrade head` when a feature requires migrations

If local Python tooling is unavailable, use the repository Docker workflow.

## Test Design

- Prefer focused pytest tests.
- Test observable behavior rather than implementation details.
- Keep fixtures simple and explicit.
- Do not skip tests unless explicitly requested and documented.
