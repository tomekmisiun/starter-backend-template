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
- uv
- Docker Compose

## Requirements

- Python 3.12
- uv
- Docker and Docker Compose
- Make

## Local Setup

Install dependencies:

```bash
make install
```

Equivalent direct command:

```bash
uv sync
```

Run locally:

```bash
make run
```

Equivalent direct command:

```bash
uv run uvicorn app.main:app --reload
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

The API image is built from `Dockerfile`, runs as a non-root `app` user, and
uses `.dockerignore` to keep local secrets, VCS metadata, virtual environments,
and cache files out of the build context.

## Environment Variables

See `.env.example` for application variables and
`.env.observability.example` for the local Grafana/Loki stack.

Required or supported application variables:

```text
DATABASE_URL=postgresql://app_user:app_password@db:5432/app_db
TEST_DATABASE_URL=postgresql://app_user:app_password@test_db:5432/app_test_db
SECRET_KEY=replace-with-a-strong-random-secret-key
ENVIRONMENT=development
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
LOG_LEVEL=INFO
RATE_LIMIT_DEFAULT_LIMIT=5
RATE_LIMIT_DEFAULT_WINDOW_SECONDS=60
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

Run tests locally with uv:

```bash
uv run pytest -v
```

The pytest setup resets the test database and applies Alembic migrations before
running tests. This validates that migrations can build the schema used by the
application tests.

Run lint:

```bash
docker compose run --rm api ruff check .
```

Run lint locally with uv:

```bash
uv run ruff check .
```

## CI

GitHub Actions builds the Docker stack, starts PostgreSQL, the test database,
and Redis, then runs Ruff and pytest in the API container. Redis-backed rate
limit tests are also run explicitly before the full test suite so Redis
integration failures are visible in CI.

## API Overview

Health:

- `GET /health`
- `GET /health/live`
- `GET /health/ready`
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

Audit log listing supports pagination and filters:

- `page`
- `size`
- `action`
- `admin_id`
- `target_user_id`

Supported audit actions:

- `user.updated`
- `user.deactivated`
- `user.activated`
- `user.deleted`

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

Current defaults are environment-driven:

- `RATE_LIMIT_DEFAULT_LIMIT=5`
- `RATE_LIMIT_DEFAULT_WINDOW_SECONDS=60`

Rate limit counters are stored in Redis by client IP and expire after the
configured window.

## Health Checks

Health endpoints are separated by deployment purpose:

- `GET /health`: backward-compatible basic process health check.
- `GET /health/live`: liveness check for process-level health.
- `GET /health/ready`: readiness check for dependencies required to serve
  traffic.
- `GET /health/db`: database dependency check.
- `GET /health/redis`: Redis dependency check.

Readiness and dependency endpoints return `200` with `status: ok` when checks
pass. Dependency failures return `503` with a consistent response body and do
not expose internal exception details.

## Error Responses

API errors use a consistent response envelope:

```json
{
  "error": {
    "code": "not_found",
    "message": "User not found"
  }
}
```

Validation errors include `details` with validation failure metadata:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed",
    "details": []
  }
}
```

The envelope preserves HTTP status codes and relevant headers such as
`WWW-Authenticate`, while avoiding internal exception details in API responses.

## Observability

Every response includes:

- `X-Request-ID`
- `X-Process-Time`

If a client sends `X-Request-ID`, the API preserves it. Otherwise, the API
generates a UUID request ID. Request start and finish events are logged with the
request ID, method, path, status code, and processing time.

Logs are written to stdout/stderr, so Docker users can inspect them with:

```bash
docker compose logs api
```

Use `LOG_LEVEL` to control the logging level.

### Local Loki/Grafana Stack

The local observability flow is:

```text
FastAPI -> stdout/stderr -> Docker logs -> Promtail -> Loki -> Grafana
```

Start the app stack and observability stack together:

```bash
docker compose -f docker-compose.yml -f docker-compose.observability.yml up --build
```

Open Grafana:

```text
http://localhost:3000
```

Default local credentials from `.env.observability`:

```text
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=admin
GF_AUTH_ANONYMOUS_ENABLED=false
```

The observability compose file loads these values from `.env.observability`.
They are not hardcoded in `docker-compose.observability.yml` and are not passed
to the API container.

Grafana provisions Loki automatically as the default datasource.

Example LogQL query:

```text
{job="fastapi"}
```

Promtail reads Docker logs from the `api` container. The application continues
to log only to stdout/stderr and does not write log files.

## Known Production Gaps

- CI does not validate migrations explicitly.
- Dependencies are mostly unpinned.
