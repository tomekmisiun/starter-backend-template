# Backend Rules

The backend stack is FastAPI, SQLAlchemy, Alembic, PostgreSQL, and Redis.

## Backend

- Keep backend code simple, explicit, and consistent with existing patterns.
- Put business logic in `app/services`.
- Keep services explicit and easy to test.
- Avoid hidden side effects unless they are part of the feature contract.
- Do not duplicate business logic across route handlers.
- Use dependencies for authentication, authorization, DB sessions, and shared
  request concerns.

## Redis

- Use Redis for explicit infrastructure concerns such as rate limiting,
  session state, revocation, and short-lived counters.
- Keep Redis configuration environment-driven.
- Add tests or focused integration coverage for Redis-backed behavior.

## Dependencies

- Do not add new libraries without explicit approval.
- Prefer existing project patterns and standard library tools when sufficient.
- Keep `requirements.txt` aligned with any approved dependency change.
