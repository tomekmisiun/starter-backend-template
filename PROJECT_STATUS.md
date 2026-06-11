# Project Status

This file preserves the current backend state and roadmap so future Codex
sessions can continue without losing context.

## 1. Current Project Status

The project is a universal, reusable FastAPI backend template for future
SaaS/API/backend projects. It is intended to be a production-ready foundation,
not a template for one specific business domain.

The current implementation is a strong local-development and testable backend
foundation using FastAPI, SQLAlchemy, Alembic, PostgreSQL, Redis, Docker
Compose, pytest, Ruff, uv, and GitHub Actions.

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
  migrations, tests, API overview, auth flow, roles, rate limiting, file
  uploads, observability, and known production gaps.

Production-readiness summary:

- The template has a broad backend feature baseline: auth/session hardening,
  users/admin flows, audit logs, rate limiting, caching, worker jobs, password
  reset, file uploads, health checks, metrics, logs, CI, and migration-aware
  tests.
- The remaining highest-value work is operational production readiness:
  deployment flow, staging/production split, secrets, backup/restore, migration
  rollout, rollback, alerting, tracing/error tracking, worker operations, and
  runbooks.
- Anything marked as a production gap below is not implemented yet unless
  explicitly listed in "Completed Features".

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
- Password reset hardening with dedicated Redis-backed rate limiting, system
  audit log entries for reset request/confirm events, and cleanup command for
  expired reset tokens.
- Redis-backed background worker, Docker Compose worker service, job retry
  handling, failed job queue, and password reset email delivery through worker
  jobs.
- Environment-driven worker scheduled maintenance for expired password reset
  token cleanup.
- Worker failed-job inspection and requeue command for Redis-backed failed
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
- Local Alertmanager service, Prometheus alert routing, and baseline FastAPI
  alert rules for target availability, 5xx error rate, and p95 latency.
- Sentry SDK error tracking and tracing foundation with environment-driven
  configuration, disabled-by-default behavior without `SENTRY_DSN`, request ID
  correlation, and regression tests without real external events.
- Pytest test suite for auth, users, admin, audit logs, and basic health.
- Migration-aware pytest setup that resets the test database and applies
  Alembic migrations before running application tests.
- Regression test confirming the test database is at the current Alembic head.
- GitHub Actions CI for Docker build, Ruff, Redis-backed rate limit tests, and
  the full pytest suite with PostgreSQL, test PostgreSQL, and Redis started.
- README documentation for project setup, API, auth flow, and production gaps.
- Provider-neutral production deployment guide covering runtime shape,
  staging/production expectations, secrets, deployment flow, migrations,
  rollback, backup/restore expectations, health checks, and smoke checks.
- Provider-neutral secret management runbook covering secret inventory,
  staging/production separation, planned rotation, emergency rotation, and
  `SECRET_KEY` rotation impact.
- Local PostgreSQL backup and restore rehearsal workflow with Makefile targets,
  ignored dump files, and provider-neutral backup/restore runbook.
- Migration and rollback support with Makefile Alembic helper targets and a
  provider-neutral migration/rollback runbook covering expand/contract,
  failed migrations, forward-fix policy, and release checklists.
- Config hardening for required non-placeholder `SECRET_KEY`, production secret
  length validation, allowed environment validation, and env-driven Redis
  settings.
- Environment/config hardening with explicit `staging` support and
  production-only validation that rejects local/default values for database,
  SMTP, password reset URL, and S3 storage settings.
- AI rules refactor with separated rules for repository, architecture, API,
  backend, database, security, testing, Docker, documentation, and git workflow.

## 3. Main Production Gaps

1. P1 - Logging is production-useful but not fully structured.
    - Request logs include request context fields and go to stdout/stderr.
    - Logs are not emitted as JSON, worker logs do not yet share a complete
      request/job correlation model, and sensitive-field redaction policy needs
      verification.

2. P1 - API versioning is not implemented.
    - Routes are mounted directly at paths such as `/auth` and `/users`; there
      is no `/api/v1` namespace or versioning policy for future breaking
      changes.

3. P1 - OpenAPI documentation quality needs improvement.
    - FastAPI generates OpenAPI automatically, but endpoint summaries,
      descriptions, examples, error envelope documentation, auth docs, and
      tag-level structure are not yet production-template quality.

4. P1 - RBAC and permissions are basic.
    - The template supports `admin` and `user`, but not a reusable permission
      model, scopes, policies, role hierarchy, or resource-level authorization
      patterns.

5. P1 - Multi-tenancy readiness is not implemented.
    - There is no tenant model, tenant-aware auth, tenant-scoped queries,
      tenant-aware audit logs, tenant-safe cache keys, or tenant isolation
      strategy.

6. P1 - Idempotency and webhook security foundation are missing.
    - The template does not yet provide idempotency keys, webhook signature
      verification, replay protection, event persistence, or generic webhook
      testing helpers.

7. P1 - File upload/storage safety is partial.
    - Upload validation, metadata storage, S3-compatible abstraction, and local
      MinIO exist.
    - Missing pieces include presigned download/upload flows, private object
      access policy, object lifecycle rules, malware scanning, content sniffing,
      bucket bootstrap verification, and storage cleanup strategy.

8. P1 - CI/CD quality is incomplete for a reusable production template.
    - CI runs Docker build, Ruff, Redis-backed tests, and pytest with database
      services.
    - Missing pieces include deployment pipeline, release artifacts, image
      tagging, vulnerability scanning, dependency review, coverage reporting,
      and optional pre-commit enforcement in CI.

9. P1 - Test coverage gaps remain around operations and scale.
    - Regression coverage is broad for current API behavior.
    - Missing coverage includes backup/restore rehearsal, deployment/migration
      failure scenarios, worker failure replay, object storage edge cases,
      OpenAPI contract checks, load/performance tests, and cache stampede or
      Redis outage behavior.

10. P2 - Dependency/version management is documented but not automated.
    - uv is configured and dependency policy is documented.
    - Automated dependency updates, vulnerability alerts, and dependency update
      cadence still require implementation or repository hosting setup.

11. P2 - Local developer experience can be improved further.
    - Makefile, Docker Compose, uv, README, and tests are in place.
    - Potential improvements include seed data, smoke-test commands, one-command
      full validation, local production-mode checks, generated API client
      examples, and clearer troubleshooting docs.

Items requiring verification before being treated as implemented:

- Production hosting target and deployment platform.
- Real production secret manager choice.
- Real backup provider and restore target.
- Whether deployment should use Kubernetes, a PaaS, Docker Compose on a VM, or
  another runtime.
- Whether the preferred error tracking/tracing stack should be Sentry,
  OpenTelemetry, or both.

## 4. Recommended Roadmap Ordered By ROI

1. P1 - API versioning and OpenAPI polish
    - Goal: make the public API contract safer to evolve across projects.
    - Recommended scope: `/api/v1` routing strategy, compatibility policy,
      OpenAPI summaries/descriptions/examples, documented error envelope, and
      regression tests for route availability.
    - Files likely to change: `app/main.py`, `app/api/routes`, `app/schemas`,
      `README.md`, `PROJECT_STATUS.md`, and `tests`.
    - Validation: `docker compose run --rm api ruff check .`,
      `docker compose run --rm api pytest -v`, and manual OpenAPI review.

2. P1 - Permission model foundation
    - Goal: evolve from two roles to reusable authorization patterns for SaaS
      projects.
    - Recommended scope: permission constants/policies, dependency helpers,
      admin/user compatibility, tests, and docs.
    - Files likely to change: `app/api/dependencies/auth.py`, `app/models`,
      `app/schemas`, `app/services`, `alembic/versions`, `README.md`,
      `PROJECT_STATUS.md`, and `tests`.
    - Validation: `docker compose run --rm api alembic upgrade head`,
      `docker compose run --rm api ruff check .`, and
      `docker compose run --rm api pytest -v`.

3. P1 - Idempotency and webhook security foundation
    - Goal: provide reusable primitives for payment providers, integrations,
      and async external events without tying the template to one provider.
    - Recommended scope: idempotency-key persistence, webhook signature helper,
      replay protection, tests, and provider-neutral documentation.
    - Files likely to change: `app/api/dependencies`, `app/models`,
      `app/services`, `app/schemas`, `alembic/versions`, `README.md`,
      `PROJECT_STATUS.md`, and `tests`.
    - Validation: `docker compose run --rm api alembic upgrade head`,
      `docker compose run --rm api ruff check .`, and
      `docker compose run --rm api pytest -v`.

4. P1 - File storage hardening
    - Goal: make uploads safer for real customer data.
    - Recommended scope: private object access, presigned URL strategy, content
      sniffing, malware scanning integration point, lifecycle/cleanup notes,
      and storage failure tests.
    - Files likely to change: `app/services/storage_service.py`,
      `app/api/routes/files.py`, `app/schemas/file.py`, `.env.example`,
      `README.md`, `PROJECT_STATUS.md`, and `tests`.
    - Validation: `docker compose run --rm api ruff check .`,
      `docker compose run --rm api pytest -v`, and MinIO local smoke test.

5. P1 - CI/CD and security scanning
    - Goal: make the template safer to maintain and release.
    - Recommended scope: Docker image scan, dependency vulnerability scan,
      coverage reporting, optional pre-commit check in CI, release image tags,
      and deployment workflow placeholder.
    - Files likely to change: `.github/workflows`, `.pre-commit-config.yaml`,
      `README.md`, `PROJECT_STATUS.md`, and possibly dependency config files.
    - Validation: GitHub Actions workflow run and local `docker compose build`.

6. P2 - Load/performance testing baseline
    - Goal: give future projects a reusable way to measure request latency,
      throughput, Redis behavior, and database pressure.
    - Recommended scope: lightweight load-test tool choice, baseline scenarios,
      local run instructions, and performance result documentation format.
    - Files likely to change: `tests` or `perf/`, `README.md`,
      `PROJECT_STATUS.md`, and optionally Docker/Makefile helpers.
    - Validation: local load-test smoke run and normal pytest/Ruff validation
      if code is added.

## 5. Next Immediate Task

Implementation should happen in a separate future branch, not on `main`.

Recommended next branch:

```text
feature/api-versioning-openapi
```

Recommended scope:

- Add `/api/v1` route namespace while preserving backward compatibility if
  needed.
- Improve OpenAPI metadata, tags, summaries, and error response documentation.
- Add route availability regression tests.
- Update `PROJECT_STATUS.md` after the task is completed.

Expected files likely to change:

- `app/main.py`
- `app/api/routes`
- `app/schemas`
- `README.md`
- `PROJECT_STATUS.md`
- `tests`

Expected validation:

- `docker compose run --rm api ruff check .`
- `docker compose run --rm api pytest -v`
- `git diff --check`

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
