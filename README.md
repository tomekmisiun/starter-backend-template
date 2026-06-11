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

## Dependency Management

Python dependencies are managed with uv:

- `pyproject.toml` defines top-level dependency constraints.
- `uv.lock` stores the resolved, reproducible dependency graph.
- Runtime dependencies belong in `[project].dependencies`.
- Test, lint, and developer tooling belongs in `[dependency-groups].dev`.

Top-level dependencies should use compatible version ranges for the current
minor line, for example `package>=1.2,<1.3`. Use exact pins only when the
project needs a known compatibility or security constraint.

When adding or updating dependencies:

1. Update `pyproject.toml`.
2. Regenerate the lockfile:

   ```bash
   uv lock
   ```

3. Sync locally if needed:

   ```bash
   uv sync
   ```

4. Run validation:

   ```bash
   docker compose build api
   docker compose run --rm api ruff check .
   docker compose run --rm api pytest -v
   ```

Commit `pyproject.toml` and `uv.lock` together after dependency changes.

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
- `worker`: Redis-backed background worker for async jobs
- `db`: main PostgreSQL database
- `test_db`: PostgreSQL database used by tests
- `redis`: Redis for rate limiting, token revocation, and background jobs
- `minio`: local S3-compatible object storage for file uploads

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
# Supported values: development, test, staging, production
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
LOG_LEVEL=INFO
RATE_LIMIT_DEFAULT_LIMIT=5
RATE_LIMIT_DEFAULT_WINDOW_SECONDS=60
PASSWORD_RESET_RATE_LIMIT_LIMIT=3
PASSWORD_RESET_RATE_LIMIT_WINDOW_SECONDS=300
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
EMAIL_FROM=noreply@example.com
PASSWORD_RESET_URL=http://localhost:8000/reset-password
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES=30
WORKER_QUEUE_NAME=app_jobs
WORKER_FAILED_QUEUE_NAME=app_jobs_failed
WORKER_POLL_TIMEOUT_SECONDS=5
WORKER_MAX_RETRIES=3
USERS_CACHE_ENABLED=true
USERS_CACHE_TTL_SECONDS=60
S3_ENDPOINT_URL=http://minio:9000
S3_ACCESS_KEY_ID=minioadmin
S3_SECRET_ACCESS_KEY=minioadmin
S3_BUCKET_NAME=uploads
S3_REGION_NAME=us-east-1
UPLOAD_MAX_SIZE_BYTES=5242880
UPLOAD_ALLOWED_CONTENT_TYPES=image/png,image/jpeg,application/pdf
SENTRY_DSN=
SENTRY_TRACES_SAMPLE_RATE=0.0
SENTRY_SEND_DEFAULT_PII=false
SENTRY_RELEASE=
```

`SECRET_KEY` is required. Known weak placeholder values such as `change-me` are
rejected. Production deployments must provide a strong secret with at least 32
characters.

Supported `ENVIRONMENT` values:

- `development`
- `test`
- `staging`
- `production`

When `ENVIRONMENT=production`, the application rejects local/default
deployment-critical placeholders. Production must provide non-local values for:

- `DATABASE_URL`
- `SMTP_HOST`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `EMAIL_FROM`
- `PASSWORD_RESET_URL`
- `S3_ENDPOINT_URL`
- `S3_ACCESS_KEY_ID`
- `S3_SECRET_ACCESS_KEY`
- `S3_BUCKET_NAME`

Use the production deployment guide for environment separation and secret
management expectations:

```text
docs/production-deployment.md
docs/secret-management.md
docs/database-backup-restore.md
docs/migration-rollback.md
```

## Migrations

Run migrations:

```bash
make migration-upgrade
```

Create a migration after a schema change:

```bash
docker compose run --rm api alembic revision --autogenerate -m "describe change"
```

Show current migration state:

```bash
make migration-current
```

Show migration heads:

```bash
make migration-heads
```

Production migration and rollback expectations are documented in:

```text
docs/migration-rollback.md
```

## Database Backup And Restore

Create a local PostgreSQL backup:

```bash
make db-backup
```

Verify that the backup can be restored into a temporary database:

```bash
make db-restore-check
```

The default dump path is `backups/app_db.dump`. Database dumps are ignored by
git and must not be committed.

Production backup and restore expectations are documented in:

```text
docs/database-backup-restore.md
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

Metrics:

- `GET /metrics`

Auth:

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `POST /auth/refresh`
- `POST /auth/logout`
- `POST /auth/password-reset/request`
- `POST /auth/password-reset/confirm`

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

Files:

- `POST /files/upload`

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
8. Request a password reset with `POST /auth/password-reset/request`.
9. Confirm the reset with `POST /auth/password-reset/confirm` using the token
   delivered by email and the new password.

Refresh token revocation is stored in Redis until the revoked token would have
expired.

Password reset requests enqueue a Redis-backed background job for email
delivery. The worker generates the raw token, sends the email, and stores only
an HMAC-SHA256 token hash in the database. Raw reset tokens are not stored in
PostgreSQL or Redis. Reset tokens are single-use and expire after
`PASSWORD_RESET_TOKEN_EXPIRE_MINUTES`. Password reset request responses do not
reveal whether an account exists or is active.

Password reset requests have dedicated Redis-backed rate limiting:

- `PASSWORD_RESET_RATE_LIMIT_LIMIT=3`
- `PASSWORD_RESET_RATE_LIMIT_WINDOW_SECONDS=300`

Password reset request and confirm events are written to audit logs as system
audit entries. Expired password reset tokens can be cleaned up with:

```bash
docker compose run --rm api python -m app.password_reset_cleanup
```

## Email

Password reset email delivery is isolated behind an email service abstraction.
The initial provider uses SMTP configuration from environment variables:

- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `EMAIL_FROM`
- `PASSWORD_RESET_URL`

`PASSWORD_RESET_URL` is used as the base URL for generated reset links. The raw
reset token is appended as a `token` query parameter and is never stored in
plaintext.

## Background Jobs

The `worker` service processes Redis-backed background jobs:

```bash
docker compose logs worker
```

Current worker-backed behavior:

- password reset email delivery

Worker configuration:

- `WORKER_QUEUE_NAME`
- `WORKER_FAILED_QUEUE_NAME`
- `WORKER_POLL_TIMEOUT_SECONDS`
- `WORKER_MAX_RETRIES`

Failed jobs are retried up to `WORKER_MAX_RETRIES`. Jobs that still fail are
moved to `WORKER_FAILED_QUEUE_NAME` for inspection. Password reset email jobs
carry only the target `user_id`; the raw reset token is generated inside the
worker and is never stored in Redis.

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

## Redis Caching

Admin user listing supports explicit Redis-backed caching. Cache keys include
the list query parameters, pagination, sorting, filters, and search value.

Current cache configuration:

- `USERS_CACHE_ENABLED=true`
- `USERS_CACHE_TTL_SECONDS=60`

The user list cache is invalidated when users are created, updated, activated,
deactivated, or deleted. Cached values expire automatically after the configured
TTL.

## File Uploads

Authenticated users can upload files with:

```text
POST /files/upload
```

Uploads are stored through an S3-compatible storage service abstraction. The
local Docker stack uses MinIO and stores file metadata in PostgreSQL.

Upload configuration:

- `S3_ENDPOINT_URL`
- `S3_ACCESS_KEY_ID`
- `S3_SECRET_ACCESS_KEY`
- `S3_BUCKET_NAME`
- `S3_REGION_NAME`
- `UPLOAD_MAX_SIZE_BYTES`
- `UPLOAD_ALLOWED_CONTENT_TYPES`

The upload endpoint validates file content type and size before writing object
metadata. Allowed content types are configured as a comma-separated list.

The local MinIO console is available at:

```text
http://localhost:9001
```

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

The API exposes Prometheus-compatible metrics at:

```text
GET /metrics
```

Current metrics include:

- `http_requests_total`
- `http_request_duration_seconds`
- `app_info`
- `process_start_time_seconds`

Request metric labels use HTTP method, route template, and status code. Route
templates such as `/users/{user_id}` are used instead of raw request paths to
avoid exposing request-specific values in metrics labels.

### Sentry Error Tracking

Sentry SDK is installed and initialized only when `SENTRY_DSN` is configured.
Without a DSN, error tracking remains disabled and no external events are sent.

Sentry configuration:

- `SENTRY_DSN`: Sentry project DSN. Empty disables Sentry.
- `SENTRY_TRACES_SAMPLE_RATE`: tracing sample rate from `0.0` to `1.0`.
- `SENTRY_SEND_DEFAULT_PII`: whether Sentry may include default PII.
- `SENTRY_RELEASE`: optional release identifier such as a git SHA or version.

The app uses the configured `ENVIRONMENT` as the Sentry environment and adds
`X-Request-ID` as a Sentry tag for request correlation.

### Local Loki/Grafana Stack

The local observability flow is:

```text
FastAPI -> stdout/stderr -> Docker logs -> Promtail -> Loki -> Grafana
FastAPI -> /metrics -> Prometheus -> Grafana
Prometheus -> Alertmanager
```

Start the app stack and observability stack together:

```bash
docker compose -f docker-compose.yml -f docker-compose.observability.yml up --build
```

Open Grafana:

```text
http://localhost:3000
```

Open Prometheus:

```text
http://localhost:9090
```

Open Alertmanager:

```text
http://localhost:9093
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

Grafana provisions Loki and Prometheus automatically as datasources. A local
`FastAPI Overview` dashboard is provisioned from
`observability/grafana/dashboards`.

Prometheus loads local alert rules from `observability/prometheus/rules` and
sends alerts to Alertmanager. The local Alertmanager receiver is intentionally
provider-neutral and does not send external notifications.

Current local alert rules:

- `FastAPITargetDown`: Prometheus cannot scrape the FastAPI metrics endpoint.
- `FastAPIHighErrorRate`: more than 5 percent of requests return 5xx responses
  over 5 minutes.
- `FastAPIHighLatencyP95`: p95 request latency is above 1 second for 5 minutes.

Production projects should replace the local receiver with the deployment
team's notification target, such as PagerDuty, Opsgenie, Slack, email, or a
cloud-native alerting integration.

Example LogQL query:

```text
{job="fastapi"}
```

Promtail reads Docker logs from the `api` container. The application continues
to log only to stdout/stderr and does not write log files.

Example PromQL query:

```text
sum by (method, path, status_code) (rate(http_requests_total[5m]))
```

## Production Deployment

This repository is a reusable backend template, not a provider-specific
deployment package. The production operating model is documented in
`docs/production-deployment.md`.

The production guide covers:

- staging and production environment expectations
- secret management expectations
- deployment and release checklist
- migration rollout strategy
- rollback strategy
- PostgreSQL backup and restore expectations
- health checks and post-deploy smoke checks

## Known Production Gaps

- Schedule automation for expired password reset token cleanup is not
  implemented.
