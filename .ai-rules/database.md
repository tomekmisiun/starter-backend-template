# Database Rules

The project uses SQLAlchemy, Alembic, PostgreSQL, and a separate test database.

## SQLAlchemy

- Use SQLAlchemy consistently.
- Prefer SQLAlchemy 2.0 style when adding new code.
- Keep models in `app/models`.
- Access the database through the existing SQLAlchemy session dependency.
- Do not hardcode database credentials.

## Alembic

- Any database schema change requires an Alembic migration.
- Do not modify existing migrations unless explicitly requested.
- Create a new migration for each schema change.
- Run `alembic upgrade head` when a feature requires migrations.
- Keep migrations reviewable and focused.

## Data Access

- Keep database access explicit.
- Avoid hiding queries inside unrelated helpers.
- Use indexes when appropriate for filtering, searching, sorting, or foreign
  keys.
- Do not mix database schema changes with unrelated refactors.
