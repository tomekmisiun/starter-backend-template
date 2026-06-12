# Project Status

Verified implementation state of the starter backend template.  
Planned work: `ROADMAP.md`. Known issues: `TECH_DEBT.md`.

Do not treat this file as a roadmap or debt register.

## Overview

Reusable FastAPI backend template for SaaS/API projects — a testable
foundation, not a finished multi-tenant SaaS platform.

**Stack:** FastAPI, SQLAlchemy, Alembic, PostgreSQL, Redis, S3-compatible
storage, Docker Compose, pytest, Ruff, uv, GitHub Actions.

**Test baseline (verified):** 304 pytest tests, ~89% line coverage, 85%
coverage floor enforced in CI and `make validate`.

**Architecture:**

- API routes: `app/api/routes`
- API dependencies: `app/api/dependencies`
- Business logic: `app/services`
- Models: `app/models`
- Schemas: `app/schemas`
- Database session: `app/db/session.py`
- Core config/security/infra: `app/core`
- Migrations: `alembic/versions` (9 revisions)
- Tests: `tests/` (43 modules)

**Documentation and rules:**

- `README.md` — setup, API, Docker, env vars, operations
- `docs/` — deployment, security, workers, tenancy, backups, load testing
- `.ai-rules/` — AI/project rules (source of truth for agent behavior)
- `AGENTS.md`, `.cursor/rules/*.mdc` — thin wrappers pointing to `.ai-rules`

---

## Verified Capabilities

### Application core

- FastAPI bootstrap with versioned API (`/api/v1`) and deprecated legacy
  unversioned routes (`app/api/legacy.py`, policy in
  `docs/legacy-route-deprecation.md`)
- Centralized error envelope for HTTP, validation, auth, not-found, and rate-limit
  responses
- Request ID middleware (`X-Request-ID`, `X-Process-Time`) with structured
  logging (`text`/`json`), sensitive-field redaction, and worker job
  `request_id` correlation
- Production/staging config validation rejecting weak secrets and local/default
  remote service placeholders (`app/core/config.py`)
- CORS, trusted hosts, and security headers middleware (env-driven)
- Optional Sentry error tracking (disabled without `SENTRY_DSN`)

### Authentication and sessions

- Registration with `REGISTRATION_POLICY` (`public` | `disabled`)
- Login with bcrypt-hashed passwords and JWT access + refresh tokens
- `/auth/me`, `/auth/refresh`, `/auth/logout`
- Refresh token rotation with Redis-backed `jti` revocation
- Access token invalidation via per-user `token_version` (password reset,
  deactivation, role change)
- Inactive users blocked on login, access, and refresh
- Redis rate limits on `/auth/login`, `/auth/register`, and password-reset
  request (per-IP; reset also keyed by email hash)
- Password reset request/confirm with hashed single-use tokens, SMTP email
  abstraction, worker job delivery, audit log entries, and expired-token
  cleanup maintenance

### Authorization and users

- RBAC roles: `user`, tenant `admin`, `platform_admin` with static permission
  map (`app/core/permissions.py`)
- Tenant `admin` excludes `tenants.*`; `platform_admin` includes tenant
  lifecycle permissions
- Admin `/admin` endpoint; user CRUD, activate/deactivate, self-read/update
- User listing with pagination, sorting, filters, and email search
- Redis-backed user-list cache with tenant-scoped keys and invalidation on writes
- Audit log model, indexes, admin listing, and writes for admin user actions

### Multi-tenancy

- Tenant model with default `default` tenant seeded in migration
- `X-Tenant-Slug` resolution for unauthenticated flows; JWT `tenant_id` on
  authenticated requests with optional header cross-check
- Tenant-scoped users (unique `(tenant_id, email)`), audit logs, uploads, cache
  keys, and object key prefixes
- Tenant lifecycle API for `platform_admin`; cross-tenant denial tests

### Files and storage

- Multipart upload and presigned upload/complete/download/delete flows
- S3-compatible storage abstraction (MinIO in local Compose)
- Size limits, content-type allowlist, magic-byte sniffing (PNG/JPEG/PDF)
- Malware scanner integration point (disabled by default; HTTP scanner or
  filename stub; documented in `docs/malware-scanning.md`)
- Private object keys under `tenants/{tenant_id}/uploads/{owner_id}/...`

### Webhooks and idempotency

- `POST /api/v1/webhooks/inbound` with timestamped HMAC verification and replay
  window
- Event deduplication on `(provider, event_id)`; payload stored as hash only
- Redis in-flight lock and persisted idempotency response cache

### Background worker

- Redis job queue with main, processing, delayed, and failed queues
- Exponential backoff retries, DLQ metadata, maintenance lock
- Password-reset email job with Redis completion marker keyed by `job.id`
- Failed-job inspection/requeue CLI (`app/worker_failed_jobs.py`)
- Docker Compose worker service

### Health and metrics

- `/health`, `/health/live`, `/health/ready` (DB + Redis), `/health/db`,
  `/health/redis`
- Prometheus `/metrics` endpoint (unauthenticated) with HTTP, dependency, and
  worker counter instrumentation in-process
- Optional Prometheus multiprocess aggregation via `PROMETHEUS_MULTIPROC_DIR`

### Local observability stack (partial)

Verified in repo:

- `docker-compose.observability.yml`
- Prometheus (`observability/prometheus/`) with scrape config and alert rules
- Loki, Promtail, Alertmanager configs
- Grafana with **Loki datasource provisioning only**

Not present in repo (README references them incorrectly — see `TECH_DEBT.md`
TD-037):

- `.env.observability.example`
- Grafana Prometheus datasource provisioning
- Provisioned Grafana dashboards

### Docker and CI/CD

- Multi-stage `Dockerfile` (development/production targets, non-root user)
- Local Compose: api, worker, db, test_db, redis, minio
- Minimal `docker-compose.prod.yml` (api + worker image only)
- CI: pre-commit, pytest with 85% coverage, backup/restore rehearsal,
  load-smoke, Trivy CRITICAL/HIGH gate, dependency review on PRs
- Release workflow (GHCR image on tag), manual deploy workflow with dry-run
  default, promotion scripts, optional migrations and smoke checks
- Dependabot for uv, GitHub Actions, and Docker base image
- Scheduled backup workflow example (requires operator secrets/hooks)

### Operations tooling

- Alembic migrations with Makefile helpers; migration downgrade rehearsal tests
- `scripts/db_backup.sh`, `db_restore_rehearsal.sh` with CI rehearsal
- `perf/load_baseline.py`, load threshold profiles, CI load-smoke job
- `make bootstrap`, `make smoke`, `make validate`, development seed data
- Runbooks in `docs/` for deployment, secrets, migrations, backups, workers,
  tenant isolation, observability, and template onboarding

---

## What this template does not include

See `ROADMAP.md` (P0–P3) and `TECH_DEBT.md` for tracked gaps. Examples:

- Production multi-worker defaults, legacy-route production gate, processing-queue
  recovery
- Proxy-aware rate limiting, metrics access control, idempotency row cleanup
- Real malware scanner, webhook processing pipeline, OAuth/MFA
- Managed hosting, secret manager, PITR, or live backup targets
- Complete local Grafana/Prometheus dashboard provisioning

---

## Updating this file

Update after merged work that changes behavior, architecture, setup, tests,
migrations, or CI.

- Add only **verified** capabilities (code + tests exist).
- Do not list planned work here — use `ROADMAP.md`.
- Do not list open defects here — use `TECH_DEBT.md`.
- Keep `.ai-rules` as the source of truth for AI behavior rules.
