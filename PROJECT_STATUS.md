# Project Status

This file preserves the current backend state and roadmap so future Codex
sessions can continue without losing context.

## 1. Current Project Status

The project is a FastAPI backend template using SQLAlchemy, Alembic,
PostgreSQL, Redis, Docker Compose, pytest, Ruff, uv, and GitHub Actions.

Current branch for active feature work: `main`.

Current architecture:

- API routes live in `app/api/routes`.
- Reusable API dependencies live in `app/api/dependencies`.
- Business logic lives in `app/services`.
- SQLAlchemy models live in `app/models`.
- Pydantic schemas live in `app/schemas`.
- Database session setup lives in `app/db/session.py`.
- Core config/security/Redis/middleware live in `app/core`.
- Alembic migrations live in `alembic/versions`.
- Regression tests live in `tests`.

Current documentation/rules setup:

- `AGENTS.md` is a minimal wrapper that points to `.ai-rules`.
- `.ai-rules` is the source of truth for AI/project rules.
- `.cursor/rules/*.mdc` files are thin wrappers pointing to `.ai-rules`.
- `README.md` documents project purpose, stack, setup, Docker, env variables,
  migrations, tests, API overview, auth flow, roles, rate limiting, and known
  production gaps.

## 2. Completed Features

- FastAPI application bootstrap with route registration.
- PostgreSQL database setup through SQLAlchemy.
- Alembic migration setup.
- Docker Compose setup for API, main database, test database, and Redis.
- Production-oriented API Dockerfile with a non-root runtime user, Python/uv
  runtime defaults, explicit build file configuration, and `.dockerignore`.
- Python dependency management through `pyproject.toml` and `uv.lock`.
- Documented dependency update policy with runtime and dev dependency
  separation.
- User registration.
- User login with access and refresh JWTs.
- Password hashing with bcrypt/passlib.
- `/auth/me` endpoint.
- `/auth/refresh` endpoint.
- `/auth/logout` endpoint.
- Password reset request and confirm endpoints with single-use hashed reset
  tokens and SMTP-backed email delivery abstraction.
- Redis-backed background worker, Docker Compose worker service, job retry
  handling, failed job queue, and password reset email delivery through worker
  jobs.
- Refresh token rotation with Redis-backed refresh token revocation.
- Inactive users are blocked from login, access-token use, and refresh-token
  use.
- Basic role-based access control with `admin` and `user` roles.
- Admin-only `/admin` endpoint.
- User listing with pagination, sorting, filtering, and email search.
- User self-read and self-update.
- Separate self-update and admin-update behavior for admin-managed fields.
- Admin user read/update/delete.
- Admin activate/deactivate user endpoints.
- Audit log model, migrations, service, admin listing endpoint, action
  constants, filtering, query indexes, and audit writes for admin user
  update/deactivate/activate/delete actions.
- Basic app health check.
- Dedicated liveness endpoint.
- Readiness endpoint that checks database and Redis dependencies.
- Database and Redis health checks with consistent `503` failure responses.
- Redis-backed example rate-limited endpoint with environment-driven defaults
  and regression coverage for limit enforcement, Redis TTLs, and per-IP
  counters.
- Redis-backed caching for admin user listing with environment-driven TTL,
  query-parameter cache keys, and invalidation after user writes.
- File upload endpoint, uploaded file metadata model, S3-compatible storage
  abstraction, local MinIO service, and upload validation for size and content
  type.
- Centralized API error response envelope for HTTP errors, validation errors,
  auth failures, not found responses, and rate limit failures.
- Request ID middleware that generates or preserves `X-Request-ID`, adds it to
  responses, keeps `X-Process-Time`, and logs request start/finish events.
- Configured stdout logging with request context fields visible in Docker logs.
- Local observability stack with Promtail, Loki, and Grafana for Docker log
  collection and inspection.
- Prometheus-compatible `/metrics` endpoint, request metrics collection,
  Prometheus service in the local observability stack, Grafana Prometheus
  datasource provisioning, and a local FastAPI overview dashboard.
- Pytest test suite for auth, users, admin, audit logs, and basic health.
- Migration-aware pytest setup that resets the test database and applies
  Alembic migrations before running application tests.
- Regression test confirming the test database is at the current Alembic head.
- GitHub Actions CI for Docker build, Ruff, Redis-backed rate limit tests, and
  the full pytest suite with PostgreSQL, test PostgreSQL, and Redis started.
- README documentation for project setup, API, auth flow, and production gaps.
- Config hardening for required non-placeholder `SECRET_KEY`, production secret
  length validation, allowed environment validation, and env-driven Redis
  settings.
- AI rules refactor with separated rules for repository, architecture, API,
  backend, database, security, testing, Docker, documentation, and git workflow.

## 3. Main Production Gaps

1. Password reset hardening follow-ups
    - Password reset does not yet include dedicated reset rate limiting, audit
      log integration, or automatic cleanup of expired tokens.

## 4. Recommended Roadmap Ordered By ROI

1. Password reset hardening follow-ups
    - Goal: harden the password reset flow beyond the baseline implementation.
    - Recommended scope: dedicated reset rate limiting, audit log integration,
      automatic cleanup of expired reset tokens, and security monitoring notes.
    - Files likely to change: `app/api/dependencies`, `app/services`,
      `app/models`, `alembic/versions`, `README.md`, `PROJECT_STATUS.md`, and
      `tests`.
    - Validation: `docker compose run --rm api ruff check .`,
      `docker compose run --rm api pytest -v`, and
      `docker compose run --rm api alembic upgrade head` if a migration is
      added.

## 5. Next Immediate Task

Implementation should happen in a separate future branch, not on `main`.

Recommended next branch:

```text
feature/password-reset-hardening
```

Recommended scope:

- Add dedicated password reset rate limiting.
- Add audit log integration for password reset events.
- Add automatic cleanup for expired password reset tokens.
- Add tests for reset rate limits, audit behavior, and cleanup behavior.
- Update README because the feature changes auth/security behavior.
- Update `PROJECT_STATUS.md` after the feature is completed.

Expected files likely to change:

- `app/api/dependencies`
- `app/services`
- `app/models`
- `alembic/versions`
- `README.md`
- `PROJECT_STATUS.md`
- `tests`

Expected validation:

- `docker compose run --rm api ruff check .`
- `docker compose run --rm api pytest -v`
- `docker compose run --rm api alembic upgrade head` if a migration is added.

## 6. Rules For Updating This File

Update `PROJECT_STATUS.md` after every completed feature before commit.

When updating this file:

- Move completed work into "Completed Features".
- Remove or rewrite production gaps that were closed.
- Adjust roadmap ordering if ROI changes.
- Update "Next Immediate Task" to the next recommended branch and scope.
- Mention any new migrations, endpoints, auth behavior, Redis behavior, Docker
  changes, or CI workflow changes.
- Keep this file factual; do not document planned work as completed.
- Keep `.ai-rules` as the source of truth for rules. This file records project
  state and roadmap, not detailed AI behavior rules.
- Do not update this file for tiny refactors that do not change behavior,
  architecture, setup, tests, docs, migrations, or production gaps.
