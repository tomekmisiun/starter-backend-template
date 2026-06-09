# Project Status

This file preserves the current backend state and roadmap so future Codex
sessions can continue without losing context.

## 1. Current Project Status

The project is a FastAPI backend template using SQLAlchemy, Alembic,
PostgreSQL, Redis, Docker Compose, pytest, Ruff, and GitHub Actions.

Current branch for active feature work: `feature/health-readiness-checks`.

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
- User registration.
- User login with access and refresh JWTs.
- Password hashing with bcrypt/passlib.
- `/auth/me` endpoint.
- `/auth/refresh` endpoint.
- `/auth/logout` endpoint.
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
- Audit log model, migration, service, admin listing endpoint, and audit writes
  for admin user update/deactivate/activate/delete actions.
- Basic app health check.
- Dedicated liveness endpoint.
- Readiness endpoint that checks database and Redis dependencies.
- Database and Redis health checks with consistent `503` failure responses.
- Redis-backed example rate-limited endpoint.
- Request ID middleware that generates or preserves `X-Request-ID`, adds it to
  responses, keeps `X-Process-Time`, and logs request start/finish events.
- Configured stdout logging with request context fields visible in Docker logs.
- Local observability stack with Promtail, Loki, and Grafana for Docker log
  collection and inspection.
- Pytest test suite for auth, users, admin, audit logs, and basic health.
- Migration-aware pytest setup that resets the test database and applies
  Alembic migrations before running application tests.
- Regression test confirming the test database is at the current Alembic head.
- GitHub Actions CI for Docker build, Ruff, and pytest.
- README documentation for project setup, API, auth flow, and production gaps.
- Config hardening for required non-placeholder `SECRET_KEY`, production secret
  length validation, allowed environment validation, and env-driven Redis
  settings.
- AI rules refactor with separated rules for repository, architecture, API,
  backend, database, security, testing, Docker, documentation, and git workflow.

## 3. Main Production Gaps

1. Redis-backed rate limit tests/config
   - Redis rate limiting exists, but it is not configurable through settings and
     has little/no regression coverage.

2. Error response standardization
    - API errors do not use a consistent response envelope.

3. Docker production hardening
    - Docker image is development-oriented.
    - It does not use a non-root runtime user or production-focused image
      hardening.

4. CI improvements
    - CI does not explicitly start Redis for Redis-backed behavior tests.

5. Audit log hardening
    - Audit actions are raw strings.
    - Audit log listing has minimal filtering.
    - Audit behavior could be made more consistent and queryable.

6. Dependency/version management
    - Most dependencies in `requirements.txt` are unpinned.
    - Reproducibility is weaker than expected for production templates.

## 4. Recommended Roadmap Ordered By ROI

1. Redis-backed rate limit tests/config
   - Goal: make rate limiting configurable and covered by tests.
   - Why: strengthens existing Redis usage and prepares for session logic.

2. Error response standardization
    - Goal: provide consistent API error responses.
    - Why: improves client experience and API professionalism.

3. Docker production hardening
    - Goal: improve image/runtime safety.
    - Why: aligns local template with production expectations.

4. CI improvements
    - Goal: validate Redis-backed tests explicitly in CI.
    - Why: catches more production-relevant failures before merge.

5. Audit log hardening
    - Goal: add action constants/enums, filtering, and stronger audit query
      behavior.
    - Why: makes admin/audit behavior more maintainable.

6. Dependency/version management
    - Goal: pin or constrain dependencies and define an update process.
    - Why: improves reproducibility.

## 5. Next Immediate Task

Recommended next branch after `feature/health-readiness-checks`:

```text
feature/rate-limit-config-tests
```

Recommended scope:

- Move rate limit values into settings.
- Add Redis-backed rate limit regression tests.
- Keep rate limit dependency explicit and reusable.
- Update README if rate limit configuration changes.

Expected files likely to change:

- `app/api/dependencies/rate_limit.py`
- `app/core/config.py`
- `.env.example`
- `tests`
- `README.md`

Expected validation:

- `ruff check .`
- `pytest`
- `alembic upgrade head` only if the implementation requires a migration.

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
