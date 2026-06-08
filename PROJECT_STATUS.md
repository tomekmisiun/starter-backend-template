# Project Status

This file preserves the current backend state and roadmap so future Codex
sessions can continue without losing context.

## 1. Current Project Status

The project is a FastAPI backend template using SQLAlchemy, Alembic,
PostgreSQL, Redis, Docker Compose, pytest, Ruff, and GitHub Actions.

Current branch for this document: `docs/project-status`.

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
- `readme.md` exists but is currently empty.
- `README.md` does not currently exist.

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
- Basic role-based access control with `admin` and `user` roles.
- Admin-only `/admin` endpoint.
- User listing with pagination, sorting, filtering, and email search.
- User self-read and self-update.
- Admin user read/update/delete.
- Admin activate/deactivate user endpoints.
- Audit log model, migration, service, admin listing endpoint, and audit writes
  for admin user update/deactivate/activate/delete actions.
- Basic app health check.
- Database health check.
- Redis health check.
- Redis-backed example rate-limited endpoint.
- Pytest test suite for auth, users, admin, audit logs, and basic health.
- GitHub Actions CI for Docker build, Ruff, and pytest.
- AI rules refactor with separated rules for repository, architecture, API,
  backend, database, security, testing, Docker, documentation, and git workflow.

## 3. Main Production Gaps

1. Auth/session hardening
   - Refresh tokens are reusable and not rotated.
   - There is no logout endpoint.
   - There is no server-side refresh token revocation.

2. Inactive user enforcement
   - Deactivated users are not consistently blocked from login or token use.

3. Separate self-update/admin-update schemas
   - The current user update schema includes `is_active`, which is an
     admin-level field and should not be available through self-update.

4. Config hardening
   - `SECRET_KEY` has an unsafe default.
   - Redis host/port are hardcoded.
   - Environment-specific config validation is minimal.

5. README/documentation
   - `readme.md` is empty and `README.md` is missing.
   - Setup, API, auth flow, roles, migrations, tests, rate limiting, and known
     production gaps are not documented for users of the template.

6. Migration-aware tests
   - Tests create tables through `Base.metadata.create_all`.
   - The test workflow does not verify that Alembic migrations produce the
     working schema.

7. Structured logging/request IDs
   - There is no request ID/correlation ID middleware.
   - Logging is not structured for production debugging.

8. Better health/readiness checks
   - Health endpoints exist, but liveness/readiness are not clearly separated.
   - Dependency failures are not wrapped in consistent responses.

9. Redis-backed rate limit tests/config
   - Redis rate limiting exists, but it is not configurable through settings and
     has little/no regression coverage.

10. Error response standardization
    - API errors do not use a consistent response envelope.

11. Docker production hardening
    - Docker image is development-oriented.
    - It does not use a non-root runtime user or production-focused image
      hardening.

12. CI improvements
    - CI does not run Alembic migration validation.
    - CI does not explicitly start Redis for Redis-backed behavior tests.

13. Audit log hardening
    - Audit actions are raw strings.
    - Audit log listing has minimal filtering.
    - Audit behavior could be made more consistent and queryable.

14. Dependency/version management
    - Most dependencies in `requirements.txt` are unpinned.
    - Reproducibility is weaker than expected for production templates.

## 4. Recommended Roadmap Ordered By ROI

1. Auth/session hardening
   - Goal: add logout, refresh token rotation, refresh revocation, and safe
     server-side session handling.
   - Why: highest security ROI and strongest production/interview value.

2. Inactive user enforcement
   - Goal: block inactive users from login, access-token use, and refresh-token
     use.
   - Why: required for account disablement to mean anything.

3. Separate self-update/admin-update schemas
   - Goal: prevent users from modifying admin-only fields through self-update.
   - Why: small change with high security and design value.

4. Config hardening
   - Goal: remove unsafe defaults, make Redis configurable, and validate
     production-critical settings.
   - Why: prevents accidental insecure deployments.

5. README/documentation
   - Goal: create a real `README.md` covering purpose, stack, setup, Docker,
     env variables, migrations, tests, API overview, auth flow, roles, rate
     limiting, and known production gaps.
   - Why: makes the template usable and reviewable.

6. Migration-aware tests
   - Goal: validate Alembic migrations in test/CI workflow.
   - Why: prevents schema drift between models and migrations.

7. Structured logging/request IDs
   - Goal: add request correlation and production-readable logs.
   - Why: improves debugging and incident response.

8. Better health/readiness checks
   - Goal: separate liveness from readiness and make dependency checks robust.
   - Why: improves deployment/runtime operations.

9. Redis-backed rate limit tests/config
   - Goal: make rate limiting configurable and covered by tests.
   - Why: strengthens existing Redis usage and prepares for session logic.

10. Error response standardization
    - Goal: provide consistent API error responses.
    - Why: improves client experience and API professionalism.

11. Docker production hardening
    - Goal: improve image/runtime safety.
    - Why: aligns local template with production expectations.

12. CI improvements
    - Goal: validate migrations and Redis-backed tests in CI.
    - Why: catches more production-relevant failures before merge.

13. Audit log hardening
    - Goal: add action constants/enums, filtering, and stronger audit query
      behavior.
    - Why: makes admin/audit behavior more maintainable.

14. Dependency/version management
    - Goal: pin or constrain dependencies and define an update process.
    - Why: improves reproducibility.

## 5. Next Immediate Task

Recommended next branch:

```text
feature/auth-session-hardening
```

Recommended scope:

- Add `POST /auth/logout`.
- Rotate refresh tokens on `/auth/refresh`.
- Invalidate old refresh tokens.
- Reject login for `is_active=False`.
- Reject access-token and refresh-token use for `is_active=False`.
- Add a self-update schema that does not include `is_active`.
- Keep admin update behavior separate from self-update behavior.
- Add regression tests for every behavior above.
- Update README documentation because auth/API behavior changes.

Expected files likely to change:

- `app/api/routes/auth.py`
- `app/api/routes/users.py`
- `app/api/dependencies/auth.py`
- `app/core/config.py`
- `app/core/redis.py`
- `app/core/security.py`
- `app/schemas/auth.py`
- `app/schemas/user.py`
- `app/services/auth_service.py`
- `app/services/user_service.py`
- `tests/test_auth.py`
- `tests/test_users.py`
- `README.md` or `readme.md`

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
