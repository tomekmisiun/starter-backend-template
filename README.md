# Starter Backend Template

FastAPI backend template for building production-oriented API services with
authentication, user management, audit logging, PostgreSQL, Redis, Docker, and
pytest.

## Tech Stack

- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Redis
- Pydantic Settings
- JWT auth with `python-jose`
- Password hashing with `passlib` and bcrypt
- pytest
- Ruff
- Docker Compose

## Requirements

- Python 3.12
- Docker and Docker Compose
- Make

## Local Setup

Install dependencies:

```bash
make install
```

Run locally:

```bash
make run
```

The app starts on `http://localhost:8000`.

## Docker Setup

Start the full local stack:

```bash
make docker-up
```

Stop the stack:

```bash
make docker-down
```

Services:

- `api`: FastAPI application
- `db`: main PostgreSQL database
- `test_db`: PostgreSQL database used by tests
- `redis`: Redis for rate limiting and token revocation

## Environment Variables

See `.env.example`.

Required or supported variables:

```text
DATABASE_URL=postgresql://app_user:app_password@db:5432/app_db
TEST_DATABASE_URL=postgresql://app_user:app_password@test_db:5432/app_test_db
SECRET_KEY=replace-with-a-strong-random-secret-key
ENVIRONMENT=development
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
```

`SECRET_KEY` is required. Known weak placeholder values such as `change-me` are
rejected. Production deployments must provide a strong secret with at least 32
characters.

Supported `ENVIRONMENT` values:

- `development`
- `test`
- `production`

## Migrations

Run migrations:

```bash
docker compose run --rm api alembic upgrade head
```

Create a migration after a schema change:

```bash
docker compose run --rm api alembic revision --autogenerate -m "describe change"
```

## Tests

Run the test suite:

```bash
docker compose run --rm api pytest -v
```

The pytest setup resets the test database and applies Alembic migrations before
running tests. This validates that migrations can build the schema used by the
application tests.

Run lint:

```bash
docker compose run --rm api ruff check .
```

## API Overview

Health:

- `GET /health`
- `GET /health/db`
- `GET /health/redis`
- `GET /health/limited`

Auth:

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `POST /auth/refresh`
- `POST /auth/logout`

Users:

- `GET /users/`
- `GET /users/{user_id}`
- `PATCH /users/{user_id}`
- `PATCH /users/{user_id}/activate`
- `PATCH /users/{user_id}/deactivate`
- `DELETE /users/{user_id}`

Admin:

- `GET /admin`
- `GET /admin/audit-logs`

## Auth Flow

1. Register with `POST /auth/register`.
2. Login with `POST /auth/login`.
3. Use the returned access token as a bearer token for protected endpoints.
4. Use the returned refresh token with `POST /auth/refresh` to receive a new
   access token and a new refresh token.
5. Refresh token rotation revokes the previous refresh token.
6. Logout with `POST /auth/logout` by sending the refresh token to revoke it.
7. Inactive users cannot log in, use access tokens, or refresh tokens.

Refresh token revocation is stored in Redis until the revoked token would have
expired.

## Roles And Permissions

Supported roles:

- `user`
- `admin`

Admin-only behavior:

- list users
- activate users
- deactivate users
- delete users
- view audit logs
- update admin-managed user fields

Regular users can read and update their own profile, but self-update does not
allow changing admin-managed fields such as `is_active`.

## Rate Limiting

`GET /health/limited` demonstrates Redis-backed IP rate limiting.

Current default:

- limit: 5 requests
- window: 60 seconds

## Known Production Gaps

- Structured logging/request IDs are not implemented.
- Health/readiness checks are basic.
- Redis-backed rate limiting needs stronger configuration and tests.
- Error response standardization is not implemented.
- Docker image is development-oriented and not hardened.
- CI does not validate migrations explicitly.
- Audit log filtering/action constants can be improved.
- Dependencies are mostly unpinned.
