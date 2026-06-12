# Starter Backend Template

FastAPI backend template for building **production-oriented API foundations**
with authentication, user management, audit logging, PostgreSQL, Redis, Docker,
and pytest.

This repository is a **production-ready foundation**, not a finished SaaS
platform. It gives you auth, workers, storage hooks, CI, and deployment
patterns; you still choose hosting, secrets, backups, and product-specific
policies.

**New project?** Start with `docs/template-onboarding.md`.

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

- Python 3.14
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

### Automated updates

Dependabot opens weekly pull requests for:

- Python dependencies in `pyproject.toml` and `uv.lock`
- GitHub Actions workflow pins
- Docker base images in `Dockerfile`

Recommended review cadence:

1. Let Dependabot group minor and patch Python updates into a small number of
   weekly PRs.
2. Wait for CI and the dependency review workflow to pass on each PR.
3. Merge patch and minor updates regularly to keep security fixes current.
4. Review major Python, Docker, and Actions updates manually because they may
   require code or infrastructure changes.

Dependabot ignores automatic major-version bumps for Python packages. Open or
approve major upgrades intentionally after reading release notes and running the
full validation commands above.

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

`Dockerfile` exposes two build targets:

- `development`: used by Docker Compose for local API/worker containers with
  pytest, Ruff, and other dev dependencies installed.
- `production`: used by CI release builds with runtime dependencies only.

Build the production image locally:

```bash
docker build --target production -t starter-backend-template-api:production .
```

### Local developer workflow

Bootstrap a fresh local environment:

```bash
make bootstrap
```

This starts Docker Compose, applies migrations, seeds development users, and
runs HTTP smoke checks against the API.

Seed development users only:

```bash
make seed
```

The seed command runs only when `ENVIRONMENT=development` and creates:

- `admin@example.local` with role `admin`
- `user@example.local` with role `user`

Both accounts use the password `devpassword123`.

Run smoke checks against a running API:

```bash
make smoke
```

Run the standard local validation workflow:

```bash
make validate
```

`make validate` runs Ruff and the full pytest suite in Docker.

Common local issues are documented in `docs/troubleshooting.md`.

Run a lightweight local load baseline:

```bash
make load-smoke
```

Run threshold-enforced load profiles and concurrency docs:

```bash
make load-validate
```

See `perf/README.md` for result format and tuning options. Concurrency regression
coverage and threshold profiles are documented in
`docs/load-concurrency-testing.md`.

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
REDIS_USERNAME=
REDIS_PASSWORD=
REDIS_SSL=false
REDIS_SSL_CERT_REQS=required
REDIS_SOCKET_TIMEOUT_SECONDS=5
REDIS_SOCKET_CONNECT_TIMEOUT_SECONDS=5
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_RECYCLE_SECONDS=1800
DB_POOL_PRE_PING=true
DB_POOL_TIMEOUT_SECONDS=30
DB_STATEMENT_TIMEOUT_MS=0
CORS_ENABLED=false
CORS_ALLOW_ORIGINS=
CORS_ALLOW_CREDENTIALS=false
CORS_ALLOW_METHODS=GET,POST,PUT,PATCH,DELETE,OPTIONS
CORS_ALLOW_HEADERS=*
TRUSTED_HOSTS_ENABLED=false
TRUSTED_HOSTS=
SECURITY_HEADERS_ENABLED=true
HSTS_ENABLED=false
HSTS_MAX_AGE_SECONDS=31536000
LOG_LEVEL=INFO
RATE_LIMIT_DEFAULT_LIMIT=5
RATE_LIMIT_DEFAULT_WINDOW_SECONDS=60
PASSWORD_RESET_RATE_LIMIT_LIMIT=3
PASSWORD_RESET_RATE_LIMIT_WINDOW_SECONDS=300
AUTH_LOGIN_RATE_LIMIT_LIMIT=10
AUTH_LOGIN_RATE_LIMIT_WINDOW_SECONDS=60
AUTH_REGISTER_RATE_LIMIT_LIMIT=5
AUTH_REGISTER_RATE_LIMIT_WINDOW_SECONDS=300
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
WORKER_MAINTENANCE_ENABLED=true
WORKER_MAINTENANCE_INTERVAL_SECONDS=3600
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
- `REDIS_HOST`
- `REDIS_PASSWORD`
- `TRUSTED_HOSTS`
- `SMTP_HOST`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `EMAIL_FROM`
- `PASSWORD_RESET_URL`
- `S3_ENDPOINT_URL`
- `S3_ACCESS_KEY_ID`
- `S3_SECRET_ACCESS_KEY`
- `S3_BUCKET_NAME`

Production also requires `TRUSTED_HOSTS_ENABLED=true`. If `CORS_ENABLED=true`,
`CORS_ALLOW_ORIGINS` must list explicit origins and must not use a wildcard.

Runtime hardening settings cover database pool sizing, Redis TLS/auth options,
security headers, CORS, and trusted host enforcement. See
`docs/production-deployment.md` for production server guidance.

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

Dry-run the automation plan without touching data:

```bash
make db-backup-dry-run
make db-restore-check-dry-run
```

The default dump path is `backups/app_db.dump`. Database dumps are ignored by
git and must not be committed.

Automation scripts, provider examples, and the manual backup rehearsal workflow
are documented in:

```text
docs/backup-restore-automation.md
```

Production backup and restore expectations are documented in:

```text
docs/database-backup-restore.md
```

## Tests

Makefile shortcuts:

```bash
make validate
make test
make test-coverage
make lint
```

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

GitHub Actions workflows:

- `ci.yml` — pre-commit, host-side pytest with an enforced 85% coverage floor,
  production Docker image build, blocking Trivy policy checks for unfixed
  `CRITICAL`/`HIGH` findings, and advisory SARIF upload to GitHub Security.
- `dependency-review.yml` — blocking pull request dependency review for runtime
  dependency changes with `high` or `critical` vulnerabilities.
- `dependabot.yml` — weekly version update PRs for uv, GitHub Actions, and Docker.
- `release.yml` — publishes tagged API images to GHCR on `v*` tags.
- `deploy.yml` — manual staging/production promotion with image verification,
  optional hook/SSH promotion, migrations, and smoke checks.

The CI pipeline starts PostgreSQL, the test database, Redis, and MinIO through
Docker Compose, then runs pytest on the GitHub runner. Coverage below 85% fails
the build. The production image build runs in parallel and must pass Trivy
policy enforcement before merge.

Local coverage run:

```bash
make test-coverage
```

This uses the same 85% coverage floor as CI.

Dry-run a deployment promotion plan locally:

```bash
make deploy-dry-run ENVIRONMENT=staging IMAGE_TAG=1.2.3
```

Release images are published to `ghcr.io/<owner>/<repository>/api:<version>`.
Configure GitHub environment secrets for hook or SSH promotion as documented in
`docs/production-deployment.md`.

## API Overview

Versioned API routes are mounted under `/api/v1`. Legacy unversioned paths such
as `/auth` and `/users` remain available for backward compatibility but are
marked deprecated in OpenAPI. New clients should use `/api/v1` exclusively.
Infrastructure endpoints (`/health`, `/metrics`) stay unversioned.

Health:

- `GET /health`
- `GET /health/live`
- `GET /health/ready`
- `GET /health/db`
- `GET /health/redis`
- `GET /health/limited`

Metrics:

- `GET /metrics`

Auth (`/api/v1/auth`):

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `POST /api/v1/auth/password-reset/request`
- `POST /api/v1/auth/password-reset/confirm`

Users (`/api/v1/users`):

- `GET /api/v1/users/`
- `GET /api/v1/users/{user_id}`
- `PATCH /api/v1/users/{user_id}`
- `PATCH /api/v1/users/{user_id}/activate`
- `PATCH /api/v1/users/{user_id}/deactivate`
- `DELETE /api/v1/users/{user_id}`

Admin (`/api/v1/admin`):

- `GET /api/v1/admin`
- `GET /api/v1/admin/audit-logs`

Files (`/api/v1/files`):

- `POST /api/v1/files/upload`

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

1. Register with `POST /api/v1/auth/register`.
2. Login with `POST /api/v1/auth/login`.
3. Use the returned access token as a bearer token for protected endpoints.
4. Use the returned refresh token with `POST /api/v1/auth/refresh` to receive a
   new access token and a new refresh token.
5. Refresh token rotation revokes the previous refresh token.
6. Logout with `POST /api/v1/auth/logout` by sending the refresh token to
   revoke it.
7. Inactive users cannot log in, use access tokens, or refresh tokens.
8. Request a password reset with `POST /api/v1/auth/password-reset/request`.
9. Confirm the reset with `POST /api/v1/auth/password-reset/confirm` using the
   token
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

Login and registration endpoints use the same Redis counter mechanism with
separate per-IP keys:

- `AUTH_LOGIN_RATE_LIMIT_LIMIT=10` (default)
- `AUTH_LOGIN_RATE_LIMIT_WINDOW_SECONDS=60`
- `AUTH_REGISTER_RATE_LIMIT_LIMIT=5`
- `AUTH_REGISTER_RATE_LIMIT_WINDOW_SECONDS=300`

Failed login attempts count toward the login limit to reduce credential
stuffing. Registration limits reduce automated account creation spam.

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
- scheduled expired password reset token cleanup

Worker configuration:

- `WORKER_QUEUE_NAME`
- `WORKER_FAILED_QUEUE_NAME`
- `WORKER_PROCESSING_QUEUE_NAME`
- `WORKER_DELAYED_QUEUE_NAME`
- `WORKER_POLL_TIMEOUT_SECONDS`
- `WORKER_MAX_RETRIES`
- `WORKER_RETRY_BACKOFF_BASE_SECONDS`
- `WORKER_RETRY_BACKOFF_MAX_SECONDS`
- `WORKER_MAINTENANCE_ENABLED`
- `WORKER_MAINTENANCE_INTERVAL_SECONDS`
- `WORKER_MAINTENANCE_LOCK_KEY`
- `WORKER_MAINTENANCE_LOCK_TTL_SECONDS`

Failed jobs are retried with exponential backoff until `WORKER_MAX_RETRIES` is
reached. Jobs move through a processing queue for acknowledgement semantics and
a delayed queue while waiting for retry backoff. Jobs that still fail are moved
to `WORKER_FAILED_QUEUE_NAME` with `last_error` and `failed_at` metadata.
Password reset email jobs carry only the target `user_id`; the raw reset token
is generated inside the worker and is never stored in Redis.

Scheduled maintenance uses a Redis lock so only one worker instance runs cleanup
during a given interval when `WORKER_MAINTENANCE_ENABLED=true`.

Worker reliability guidance lives in:

```text
docs/worker-reliability.md
```

Inspect failed jobs:

```bash
docker compose run --rm worker python -m app.worker_failed_jobs list
```

Requeue failed jobs:

```bash
docker compose run --rm worker python -m app.worker_failed_jobs requeue
```

## Roles And Permissions

Supported roles:

- `user`
- `admin`

Authorization is permission-based. Roles map to permission policies in
`app/core/permissions.py`, and routes use `require_permission(...)` or
resource-level helpers from `app/services/permission_service.py`.

Examples:

- `users.list`, `users.read`, `users.update`, `users.delete`
- `users.read.self`, `users.update.self`
- `users.activate`, `users.deactivate`
- `admin.access`, `audit_logs.list`, `files.upload`, `files.download.self`,
  `files.delete.self`

`admin` inherits the `user` role hierarchy and receives the full permission
set. Regular users can read and update only their own profile through self
permissions, but self-update does not allow changing admin-managed fields such
as `is_active`.

## Idempotency And Webhooks

The template includes provider-neutral primitives for safe external integrations:

- `Idempotency-Key` persistence through `idempotency_records` for replay-safe
  response caching with Redis-backed in-flight duplicate protection.
- `POST /api/v1/webhooks/inbound` with timestamped HMAC verification using
  `X-Webhook-Timestamp` and `X-Webhook-Signature`.
- `webhook_events` persistence for replay protection by `(provider, event_id)`.
- Stripe-style combined signatures (`t=...,v1=...`) are also supported.

Configure `WEBHOOK_SIGNATURE_SECRET`, `WEBHOOK_SIGNATURE_TOLERANCE_SECONDS`, and
see `docs/webhook-idempotency.md` for provider-specific patterns.

## Multi-Tenancy

The template includes tenant-aware data isolation:

- `tenants` table with a seeded `default` tenant for local development.
- Users, audit logs, uploads, cache keys, and object storage keys are scoped by
  `tenant_id`.
- Auth endpoints resolve the tenant from `X-Tenant-Slug` (default: `default`).
- JWT access and refresh tokens include `tenant_id` and are validated against
  the user's tenant on every authenticated request.
- Authenticated requests reject mismatched `X-Tenant-Slug` headers and inactive
  tenant memberships.
- Admin tenant lifecycle endpoints support provisioning, listing, and
  activation/deactivation. See `docs/tenant-isolation.md`.

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

Authenticated users can upload and access private files through:

- `POST /api/v1/files/upload` — multipart upload with content sniffing
- `POST /api/v1/files/presigned-upload` — short-lived PUT URL for direct uploads
- `POST /api/v1/files/presigned-upload/complete` — register a presigned upload
- `GET /api/v1/files/{file_id}/download-url` — short-lived private download URL
- `DELETE /api/v1/files/{file_id}` — delete object metadata and storage object

Uploads are stored through an S3-compatible storage service abstraction. The
local Docker stack uses MinIO and stores file metadata in PostgreSQL. Objects
are private; clients use presigned URLs for download access.

Upload configuration:

- `S3_ENDPOINT_URL`
- `S3_ACCESS_KEY_ID`
- `S3_SECRET_ACCESS_KEY`
- `S3_BUCKET_NAME`
- `S3_REGION_NAME`
- `UPLOAD_MAX_SIZE_BYTES`
- `UPLOAD_ALLOWED_CONTENT_TYPES`
- `UPLOAD_PRESIGNED_URL_EXPIRE_SECONDS`
- `UPLOAD_STREAM_CHUNK_SIZE_BYTES`
- `UPLOAD_MALWARE_SCAN_ENABLED`
- `UPLOAD_MALWARE_SCANNER_URL`
- `UPLOAD_MALWARE_SCANNER_TIMEOUT_SECONDS`

The upload flow validates filename metadata, declared content type, file size,
magic-byte content sniffing, and malware scanning before writing metadata.
Presigned completion verifies the stored object size, content type, sniffed
bytes, and scan result before metadata is persisted. See
`docs/file-upload-production.md` for production guidance and scanner integration
boundaries.

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
- `worker_jobs_total`
- `worker_maintenance_runs_total`
- `dependency_checks_total`
- `dependency_health_status`
- `app_info`

Observability configuration:

- `PROMETHEUS_MULTIPROC_DIR`: shared directory for multi-worker Uvicorn metrics
- `METRICS_INSTANCE_ID`: optional per-replica identifier label

Request metric labels use HTTP method, route template, and status code. Route
templates such as `/users/{user_id}` are used instead of raw request paths to
avoid exposing request-specific values in metrics labels.

Production observability guidance lives in:

```text
docs/observability-production.md
```

### Sentry Error Tracking

Sentry SDK is installed and initialized only when `SENTRY_DSN` is configured.
Without a DSN, error tracking remains disabled and no external events are sent.

Sentry configuration:

- `SENTRY_DSN`: Sentry project DSN. Empty disables Sentry.
- `SENTRY_TRACES_SAMPLE_RATE`: tracing sample rate from `0.0` to `1.0`.
- `SENTRY_SEND_DEFAULT_PII`: whether Sentry may include default PII.
- `SENTRY_RELEASE`: optional release identifier such as a git SHA or version.

The app uses the configured `ENVIRONMENT` as the Sentry environment and adds
request correlation through the `request_id` tag and Sentry request context.

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

The template ships implementation patterns and runbooks, but **not** a fully
configured production environment. Before launch, each downstream project must
still decide and wire up:

- production hosting target and runtime (Kubernetes, PaaS, VM, etc.)
- secret manager and rotation policy
- managed PostgreSQL, Redis, and object storage
- backup provider, RPO/RTO, and PITR policy (logical backup scripts exist;
  PITR is provider-specific)
- tracing stack preference (Sentry, OpenTelemetry, or both)
- GitHub Environment secrets for deploy workflows

Template hardening work tracked in `PROJECT_STATUS.md` includes worker
idempotency, staging config parity, platform vs tenant admin boundaries,
registration policy gates, access-token invalidation strategy, and related
docs/tests.

See `docs/template-onboarding.md` for the full clone → local → staging path.
