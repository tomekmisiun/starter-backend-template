# Technical Debt Register

Identified from the June 2026 production audits (implementation review only).
Each item is an open engineering debt unless marked **Done** with code verification.

For prioritized remediation order, see `ROADMAP.md`.  
For verified current capabilities, see `PROJECT_STATUS.md`.

**Status legend:** Open | In Progress | Done

---

## Critical

| ID | Issue | Impact | Recommendation | Effort | Status |
|----|-------|--------|----------------|--------|--------|
| TD-001 | Production Docker image runs single-process Uvicorn (`Dockerfile` CMD, no `--workers`). | One CPU core serves all traffic; auth path saturates under login spikes. | Document and encode multi-worker deployment (gunicorn+uvicorn workers or horizontal scaling with sizing guide). | M | Done |
| TD-002 | Legacy API router remounts auth/users/admin/tenants/files at unversioned paths (`app/api/legacy.py`, `app/main.py`). | Doubles protected attack surface; forks forget to remove deprecated routes. | Gate behind env flag (default off in production) or remove in next major version. | S | Done |
| TD-003 | Worker processing queue has no visibility timeout or reaper (`brpoplpush` in `app/core/job_queue.py`). | Worker crash/OOM during deploy leaves jobs stuck in `app_jobs_processing` forever. | Add stale-job reclaim (visibility timeout, heartbeat, or periodic reaper). | M | Done |
| TD-004 | Hard dependency on Redis with no degradation policy (rate limits, refresh rotation, cache, idempotency locks, job queue). | Redis blip causes auth failures, 429/500 cascades, and queue stall across the system. | Define fail-open vs fail-closed per feature; add circuit breaker and Redis HA guidance. | L | Open |

---

## High

| ID | Issue | Impact | Recommendation | Effort | Status |
|----|-------|--------|----------------|--------|--------|
| TD-005 | `/metrics` is unauthenticated (`app/api/routes/metrics.py`). | Traffic patterns and dependency health leak if exposed beyond internal network. | Restrict via network ACL, mTLS, or auth middleware; document requirement. | S | Done |
| TD-006 | Rate limits key on `request.client.host` only (`app/api/dependencies/rate_limit.py`). | Behind reverse proxy: limits are ineffective or block all users on one IP. | Parse trusted forwarded headers; align with Uvicorn `--proxy-headers` and allowlist. | M | Done |
| TD-007 | JWT encode uses hardcoded `ALGORITHM`; decode uses `settings.algorithm` (`app/core/security.py`). | Misconfigured env breaks auth or creates inconsistent token validation. | Single source of truth for signing algorithm. | S | Done |
| TD-008 | `UserAdminUpdate.role` accepts arbitrary strings (`app/schemas/user.py`). | Invalid roles get empty permissions or accidental lockout. | Validate against allowed role enum in schema/service. | S | Open |
| TD-009 | Malware scanning disabled by default; fallback scanner checks filename only (`app/core/config.py`, `app/services/malware_scanner.py`). | Malicious uploads stored if forks enable files without wiring a scanner. | Fail production startup when uploads enabled without real scanner URL. | S | Open |
| TD-010 | Idempotency records expire logically but are never deleted (`app/services/idempotency_service.py`). | Table bloat slows lookups and increases backup/storage cost. | Scheduled purge of rows where `expires_at < now()`. | S | Open |
| TD-011 | Unknown worker job types log a warning then are acknowledged (`app/worker.py`). | Schema drift or typos silently drop jobs. | Route unknown types to DLQ instead of ack. | S | Open |
| TD-012 | Nearly all routes are sync `def` with sync SQLAlchemy sessions. | Thread pool exhaustion under concurrent DB-bound load before DB maxes out. | Async SQLAlchemy + async routes, or explicit multi-worker sync sizing. | XL | Open |
| TD-013 | Default DB pool (`pool_size=5`, `max_overflow=10`) with no startup visibility. | Naive horizontal scaling exhausts Postgres `max_connections`. | Log effective pool; document `(workers × replicas × pool)` formula. | S | Done |
| TD-014 | Refresh tokens omit `token_version` (`app/core/security.py`). | Compromised refresh remains valid until rotation after role change/password reset. | Embed and validate `token_version` on refresh. | M | Open |
| TD-015 | `/auth/refresh` and `/auth/logout` have no rate limits (`app/api/routes/auth.py`). | Refresh grinding amplifies Redis and DB load. | Add per-IP and per-token-hash limits. | S | Open |

---

## Medium

| ID | Issue | Impact | Recommendation | Effort | Status |
|----|-------|--------|----------------|--------|--------|
| TD-016 | No Docker `HEALTHCHECK` or compose healthchecks. | Orchestrators route traffic to hung containers; slow incident detection. | Add healthcheck hitting `/health/live`; wire compose conditions. | S | Open |
| TD-017 | No graceful shutdown for API or worker (`app/worker.py`, `app/main.py`). | Deployments drop in-flight work; jobs remain in processing queue. | SIGTERM handlers, drain timeout, FastAPI lifespan hooks. | M | Open |
| TD-018 | Python 3.14 base image (`Dockerfile`). | Hosting/ecosystem lag across hundreds of forks. | Pin to 3.12/3.13 LTS unless 3.14 is intentional. | S | Open |
| TD-019 | Webhook ingress has no rate limit or max body size (`app/api/routes/webhooks.py`). | DoS via large payloads or high request volume. | Body size middleware; rate limit by provider/IP. | S | Open |
| TD-020 | No global handler for unhandled exceptions (`app/main.py`). | Possible internal detail leakage depending on debug settings. | Generic 500 handler; enforce `debug=False` in production docs. | S | Open |
| TD-021 | Tenant isolation is application-layer only (no PostgreSQL RLS). | Raw SQL or ORM bypass in forks can cross tenants. | Document requirement; optional RLS migration example. | L | Open |
| TD-022 | Password-reset worker idempotency marker set after DB commit (`app/services/password_reset_service.py`). | Crash between commit and Redis SET can duplicate tokens/emails on retry. | DB-level idempotency keyed by `job_id` or reorder side effects. | M | Open |
| TD-023 | Worker Prometheus metrics not scrapeable in default prod layout (metrics HTTP on API only). | Silent worker/backlog failures in operations. | Sidecar exporter, pushgateway, or shared `PROMETHEUS_MULTIPROC_DIR`. | M | Open |
| TD-024 | `webhook_events` table is insert-only with no retention (`app/services/webhook_service.py`). | Storage and query cost grow unbounded on high-volume forks. | Retention job and archival policy. | S | Open |
| TD-025 | Audit logs are append-only with no retention (`app/services/audit_log_service.py`). | Admin queries slow; compliance storage grows. | Partition or export-to-cold-storage job. | M | Open |
| TD-026 | User and audit lists use offset pagination (`app/api/routes/users.py`). | Deep pages become expensive at large tenant sizes. | Keyset/cursor pagination. | M | Open |
| TD-027 | User email search uses `%term%` ILIKE (`app/services/user_service.py`). | Sequential scans under admin search load. | Trigram index or prefix-only search. | M | Open |
| TD-028 | User list cache invalidation uses Redis `SCAN` + bulk delete (`app/core/cache.py`). | Redis CPU spikes under high admin write churn. | Versioned cache keys or tag-based invalidation. | M | Open |
| TD-029 | New boto3 S3 client created per request (`get_storage_service()` in `app/services/storage_service.py`). | Connection overhead on file endpoints under concurrency. | Lifespan-cached or module-level client. | S | Open |
| TD-030 | Direct uploads buffer entire file in memory (`read_upload_body_limited`). | Memory spikes with concurrent max-size uploads. | Stream to S3 multipart upload. | M | Open |
| TD-031 | Presigned upload complete re-downloads object from S3 for sniff/scan. | 2× bandwidth; API acts as proxy at scale. | Scan at bucket edge or async worker. | M | Open |
| TD-032 | Readiness checks DB and Redis only, not S3 (`app/api/routes/health.py`). | Load balancer marks ready while uploads fail at runtime. | Optional S3 head-bucket in readiness when file features enabled. | S | Open |
| TD-033 | User update and audit log are separate DB commits (`app/api/routes/users.py`). | User changed without audit row on partial failure. | Single transaction or outbox pattern. | M | Open |
| TD-034 | Tenant `ContextVar` tokens stored but never reset (`app/api/dependencies/tenant.py`). | Stale tenant context under thread-reuse edge cases. | Reset in middleware `finally`. | S | Open |
| TD-035 | CI `docker-build` job does not depend on `test` (`.github/workflows/ci.yml`). | Image can pass Trivy while tests fail on same commit. | Add `needs: [test]`. | S | Open |
| TD-036 | Scheduled backup workflow exits successfully when secrets are missing. | False confidence that backups run. | Fail cron when required secrets absent. | S | Open |
| TD-037 | Observability docs reference missing assets (`.env.observability.example`, Grafana Prometheus datasource, dashboards). | Hundreds of clones waste time on broken local observability setup. | Add files or remove incorrect README/PROJECT_STATUS claims. | M | Open |
| TD-038 | Promtail config hardcodes Docker container name (`observability/promtail/promtail.yml`). | Log collection fails after compose project rename. | Use compose service discovery labels. | S | Open |
| TD-039 | Tenant `default` seeded with fixed `id=1` in migration (`a1b2c3d4e5f6`). | Migration/assumption conflicts in multi-environment clones. | Seed via app command instead of migration bulk insert. | M | Open |
| TD-040 | `platform_admin` is a tenant-bound user row, not a separate operator model. | Every fork re-implements operator/security model. | Separate operator table or explicit demo-only documentation. | L | Open |
| TD-041 | Services raise `HTTPException` directly throughout service layer. | Hard to reuse from workers/CLI; inconsistent error handling in forks. | Domain exceptions translated at route boundary. | L | Open |
| TD-042 | Worker loop runs maintenance and `promote_delayed_jobs` on every iteration. | Redis overhead under high queue depth. | Separate maintenance ticker; batch promote with limits. | S | Open |
| TD-043 | Possible double migration on deploy (SSH script + runner `deploy_migrate.sh`). | Redundant Alembic runs confuse runbooks. | Deduplicate migration step in deploy workflow. | S | Open |
| TD-044 | `release.yml` publishes `latest` tag while production deploy discourages it. | Easy misuse of mutable tag in production. | Document tension or stop tagging `latest`. | S | Open |
| TD-045 | `BaseHTTPMiddleware` used for request logging (`app/core/middleware.py`). | Extra latency under high load (known Starlette overhead). | Pure ASGI middleware. | M | Open |
| TD-046 | JWT access/refresh TTLs hardcoded (30 min / 7 days). | Product policy changes require code edits across forks. | Env-driven TTL settings. | S | Open |
| TD-047 | Duplicate `UserRead` schema in `app/schemas/auth.py` and `app/schemas/user.py`. | API contract drift risk. | Consolidate to single schema module. | S | Open |
| TD-048 | Alertmanager receiver is empty stub (`observability/alertmanager/alertmanager.yml`). | Local alerts go nowhere; forks assume routing works. | Document as stub; provide example receiver config. | S | Open |

---

## Low

| ID | Issue | Impact | Recommendation | Effort | Status |
|----|-------|--------|----------------|--------|--------|
| TD-049 | No `Content-Security-Policy` header (API-only template). | Minor for JSON APIs; relevant if HTML error pages served. | Add CSP when serving HTML. | S | Open |
| TD-050 | No OpenTelemetry integration. | Limited distributed tracing beyond optional Sentry. | Document as downstream choice or add optional OTel hook. | L | Open |
| TD-051 | No adversarial security test suite (JWT tampering, upload fuzzing). | Regressions in security controls may slip through. | Add targeted security regression tests. | M | Open |
| TD-052 | No end-to-end Docker test for api+worker+redis email flow. | Worker integration bugs found only in production. | Compose-based integration test in CI. | M | Open |
| TD-053 | Deploy/smoke scripts (`smoke_test.sh`, `deploy_remote_compose.sh`) lack unit tests. | Script regressions undetected until manual deploy. | Add script dry-run tests. | S | Open |
| TD-054 | Observability stack not validated in CI. | Broken Prometheus/alert rules merge unnoticed. | Optional CI job to lint prom rules / compose config. | M | Open |
| TD-055 | Migration tests cover one-step downgrade only. | Multi-revision rollback scenarios untested. | Extend migration rehearsal tests. | M | Open |
| TD-056 | Low coverage in `email_service.py`, `storage_service.py`, `db/session.py`. | Regressions in infra adapters less likely caught. | Add targeted unit/integration tests. | M | Open |

---

## Summary

| Severity | Open items |
|----------|------------|
| Critical | 4 |
| High | 11 |
| Medium | 33 |
| Low | 8 |
| **Total** | **56** |

All items are **Open** as of the last codebase verification (304 tests, June 2026 audit).
