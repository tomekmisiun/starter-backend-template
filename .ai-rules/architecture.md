# Architecture Rules

This project is a FastAPI backend template using SQLAlchemy, Alembic,
PostgreSQL, and Redis. Preserve the current architecture unless an explicit
task requires changing it.

## Layers

- `app/api/routes`: HTTP endpoints, routing, status codes, response models, and
  request dependency wiring.
- `app/api/dependencies`: reusable FastAPI dependencies, including auth,
  authorization, database access dependencies, and rate limiting.
- `app/services`: business logic and application workflows.
- `app/models`: SQLAlchemy database models.
- `app/schemas`: Pydantic request and response schemas.
- `app/db/session.py`: SQLAlchemy engine, session factory, and DB session
  dependency.
- `app/core/config.py`: environment-driven application configuration.
- `app/core/security.py`: password hashing, token creation, and security helper
  functions.
- `alembic/versions`: database schema migrations.
- `tests`: pytest regression tests for API and service behavior.

## Rules

- Keep route handlers thin.
- Put business logic in services.
- Put request and response validation in schemas.
- Access the database through SQLAlchemy sessions.
- Any database schema change requires an Alembic migration.
- Do not mix authentication/session logic with unrelated business logic.
- Keep auth dependencies reusable and explicit.
- Do not add new libraries without explicit approval.
- Follow existing project naming, structure, and dependency injection patterns.
