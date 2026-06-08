# Backend Rules

The backend stack is FastAPI, SQLAlchemy, Alembic, PostgreSQL, and Redis.

## FastAPI

- Keep routers separated by domain.
- Keep route handlers thin and predictable.
- Use dependencies for authentication, authorization, DB sessions, and shared
  request concerns.
- Use Pydantic schemas for request and response validation.
- Use clear response models.
- Use proper HTTP status codes.
- Raise `HTTPException` for API errors.
- Do not expose internal implementation errors to API clients.

## Services

- Put business logic in `app/services`.
- Keep services explicit and easy to test.
- Avoid hidden side effects unless they are part of the feature contract.
- Do not duplicate business logic across route handlers.

## Database

- Use SQLAlchemy consistently.
- Keep models in `app/models`.
- Keep schema validation in `app/schemas`.
- Use the existing SQLAlchemy session dependency for database access.
- Any schema change requires an Alembic migration.
- Do not hardcode database credentials.

## Redis

- Use Redis for explicit infrastructure concerns such as rate limiting,
  session state, revocation, and short-lived counters.
- Keep Redis configuration environment-driven.
- Add tests or focused integration coverage for Redis-backed behavior.

## Dependencies

- Do not add new libraries without explicit approval.
- Prefer existing project patterns and standard library tools when sufficient.
- Keep `requirements.txt` aligned with any approved dependency change.
