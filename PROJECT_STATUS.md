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

Current branch for active feature work:
`feature/observability-production-hardening`.

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
- The project is a strong universal FastAPI backend template foundation, but it
  is not yet fully production-ready for high-scale SaaS/API workloads.
  Remaining work is concentrated around production runtime hardening,
  deployment automation, worker reliability, production observability, tenant
  isolation, storage safety, CI enforcement, and recovery automation.
- Anything not listed in "Completed Features" should be treated as not
  implemented unless a new roadmap item is added explicitly.

## 2. Completed Features

- FastAPI application bootstrap with route registration.
- PostgreSQL database setup through SQLAlchemy.
- Alembic migration setup.
- Docker Compose setup for API, main database, test database, and Redis.
- Production-oriented API Dockerfile with non-root runtime user, Python/uv
  defaults, `.dockerignore`, separate `development` and `production` build
  targets, production-only runtime dependencies, and a production Uvicorn
  entrypoint documented in `docs/production-deployment.md`.
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
  handling with exponential backoff, processing and delayed queues, failed job
  dead-letter metadata, Redis-backed maintenance locking, failed job queue, and
  password reset email delivery through worker jobs.
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
- Structured logging foundation with env-driven `text`/`json` output, sensitive
  field redaction, request/job correlation via `request_id` propagation into
  worker jobs, and regression tests for formatters and redaction policy.
- API versioning with `/api/v1` route namespace, deprecated legacy route
  compatibility for existing unversioned paths, and route availability
  regression tests.
- OpenAPI documentation polish with tag descriptions, endpoint summaries,
  documented error envelope schema, bearer auth scheme, request examples, and
  contract regression tests.
- Reusable permission model with role-to-permission policies, role hierarchy,
  `require_permission` dependency helpers, resource-level user authorization
  helpers, and regression tests while preserving existing `admin`/`user` roles.
- Multi-tenancy foundation with tenant model/migration, `X-Tenant-Slug` auth
  resolution, tenant-scoped users/audit logs/uploads, tenant-safe cache/object
  key prefixes, JWT tenant claims, and regression tests. This is a foundation,
  not a complete SaaS tenant isolation model.
- Idempotency and webhook security foundation with persisted idempotency keys,
  signed inbound webhook endpoint, replay-protected webhook event storage, and
  regression tests.
- File storage hardening foundation with private object uploads, presigned
  download/upload flows, content sniffing, malware-scan integration point,
  bucket access verification, delete cleanup, and storage failure regression
  tests. The malware scanner remains an integration point until a concrete
  scanner/provider is wired in by a downstream project.
- CI/CD quality foundation with pre-commit enforcement, pytest coverage
  artifacts, enforced coverage floor, blocking Trivy image policy checks,
  advisory SARIF upload, blocking runtime dependency review on pull requests,
  GHCR release image publishing, and a manual GitHub Actions deploy workflow
  with hook/SSH promotion, optional migrations, and smoke checks.
- Operations and scale regression coverage for migration downgrade/upgrade
  rehearsal, logical backup/restore rehearsal, worker failed-job CLI replay,
  Redis outage behavior, cache-miss consistency, and OpenAPI contract checks.
- Dependabot automation for weekly uv, GitHub Actions, and Docker image update
  pull requests with documented review cadence in `README.md`.
- Local developer experience improvements with development-only seed data,
  `make bootstrap`, `make smoke`, `make validate`, and troubleshooting docs.
- Lightweight load/performance baseline with `perf/load_baseline.py`,
  `make load-smoke`, and documented JSON result format.
- Local observability stack with Promtail, Loki, and Grafana for Docker log
  collection and inspection.
- Prometheus-compatible `/metrics` endpoint, request metrics collection,
  worker and dependency metrics, optional multi-process aggregation, Sentry
  request correlation, Prometheus service in the local observability stack,
  Grafana Prometheus datasource provisioning, and a local FastAPI overview
  dashboard.
- Local Alertmanager service, Prometheus alert routing, and baseline FastAPI
  alert rules for target availability, 5xx error rate, and p95 latency.
- Sentry SDK error tracking and tracing foundation with environment-driven
  configuration, disabled-by-default behavior without `SENTRY_DSN`, request ID
  correlation, and regression tests without real external events. This is not a
  complete distributed tracing or incident-response setup.
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
  ignored dump files, and provider-neutral backup/restore runbook. Production
  backup automation, PITR, and provider-specific restore drills remain
  downstream responsibilities.
- Migration and rollback support with Makefile Alembic helper targets and a
  provider-neutral migration/rollback runbook covering expand/contract,
  failed migrations, forward-fix policy, and release checklists.
- Config hardening for required non-placeholder `SECRET_KEY`, production secret
  length validation, allowed environment validation, and env-driven Redis
  settings.
- Environment/config hardening with explicit `staging` support and
  production-only validation that rejects local/default values for database,
  SMTP, password reset URL, and S3 storage settings.
- Production runtime hardening with environment-driven database pool settings,
  Redis auth/TLS/timeouts, CORS and trusted host middleware, security headers,
  production validation for Redis and trusted hosts, and production server
  guidance in `docs/production-deployment.md`.
- Production deployment automation with a manual GitHub Actions workflow,
  provider-neutral promotion scripts for deploy hooks and SSH compose rollout,
  optional runner-side Alembic migrations, post-deploy smoke checks, and
  `docker-compose.prod.yml` for VM-style deployments.
- Worker reliability improvements with processing acknowledgement, delayed retry
  backoff, dead-letter metadata, Redis-backed maintenance locking, failed-job
  CLI metadata output, and `docs/worker-reliability.md`.
- Production observability hardening with `prometheus-client` metrics,
  multi-process aggregation support, worker and dependency metrics, Sentry
  request correlation, and `docs/observability-production.md`.
- Tenant isolation hardening with membership validation on authenticated
  requests, inactive-tenant rejection, admin tenant lifecycle endpoints,
  tenant-management permissions, cross-tenant denial regression tests, and
  `docs/tenant-isolation.md`.
- Webhook and idempotency hardening with timestamped HMAC verification, replay
  windows, Redis-backed in-flight idempotency locking, concurrent duplicate
  fallback handling, production webhook secret validation, and
  `docs/webhook-idempotency.md`.
- File upload production hardening with streaming-safe multipart reads, stored
  object verification after presigned uploads, metadata validation, HTTP
  malware scanner integration boundaries, and `docs/file-upload-production.md`.
- AI rules refactor with separated rules for repository, architecture, API,
  backend, database, security, testing, Docker, documentation, and git workflow.

## 3. Main Production Gaps

The project should still be treated as a production-ready template foundation,
not a finished production platform. The following gaps are template-wide enough
to track before calling the repository complete for high-scale reuse.

- P2: Disaster recovery automation.
  Backup/restore docs and local rehearsal exist, but production provider
  automation, PITR strategy, and automated restore rehearsal remain
  project-specific gaps.

- P2: Load, performance, and concurrency testing.
  The repository has a lightweight baseline, but needs repeatable thresholds and
  race-condition coverage for idempotency, workers, auth/session behavior,
  Redis, storage, and high-latency dependencies.

Items requiring verification before being treated as implemented:

- Production hosting target and deployment platform.
- Real production secret manager choice.
- Real backup provider, PITR policy, and restore target.
- Whether deployment should use Kubernetes, a PaaS, Docker Compose on a VM, or
  another runtime.
- Whether the preferred production tracing stack should be Sentry,
  OpenTelemetry, or both.

## 4. Recommended Roadmap Ordered By ROI

Template-wide roadmap items should be completed on separate branches. Do not
mark them as completed until the implementation and regression coverage are on
`main`.

| Priority | Item | Goal | Recommended branch |
|----------|------|------|--------------------|
| P2 | Backup/restore automation | Add provider-ready backup automation examples and stronger restore rehearsal workflows. | `feature/backup-restore-automation` |
| P2 | Load and concurrency testing | Add repeatable performance thresholds and concurrency tests for critical infrastructure paths. | `feature/load-concurrency-testing` |

## 5. Next Immediate Task

Implementation should happen in a separate future branch, not on `main`.

Recommended next branch:

```text
feature/backup-restore-automation
```

Recommended scope:

- Add provider-ready backup automation examples.
- Strengthen restore rehearsal workflows and operational guidance.

Expected validation:

- `make validate`
- Backup/restore rehearsal tests for changed paths

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
