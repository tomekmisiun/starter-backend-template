# Tenant Isolation

This template uses single-tenant membership per user account. Each user row
belongs to exactly one tenant through `users.tenant_id`, and all tenant-scoped
data paths validate that membership before returning or mutating data.

## Request Boundaries

Tenant context is resolved in two places:

- Public auth flows resolve the tenant from `X-Tenant-Slug` (default: `default`).
- Authenticated requests validate JWT `tenant_id` against the loaded user row.

When an authenticated request includes `X-Tenant-Slug`, the header must match
the user's tenant. A mismatch returns `403 Tenant access denied` even if the
JWT is otherwise valid.

Inactive tenants are rejected for authenticated access and refresh-token
rotation.

## Authorization Layers

Tenant isolation is enforced at multiple layers:

1. JWT claims include `tenant_id` and are validated on every authenticated
   request.
2. Service helpers such as `users_share_tenant()` deny cross-tenant reads and
   updates.
3. Storage, audit logs, cache keys, and object keys are namespaced by tenant.
4. Admin tenant provisioning endpoints require explicit tenant-management
   permissions.

## Provisioning Lifecycle

Recommended lifecycle for new tenants:

1. Provision the tenant with `POST /api/v1/admin/tenants`.
2. Share the tenant slug with the customer application.
3. Register or invite users through `/api/v1/auth/register` with
   `X-Tenant-Slug: <tenant-slug>`.
4. Deactivate the tenant with `PATCH /api/v1/admin/tenants/{tenant_id}` when
   the customer offboards.

Provisioning and lifecycle changes are audit logged in the provisioning
admin's tenant audit stream.

## Admin Permissions

Tenant lifecycle endpoints require admin permissions:

- `tenants.list` for listing and reading tenants
- `tenants.provision` for creating tenants
- `tenants.manage` for activation/deactivation and metadata updates

Regular `user` role accounts cannot access tenant lifecycle endpoints.

## Regression Expectations

When extending tenant-aware features, keep these guarantees:

- Cross-tenant user reads and updates must return `403` or `404`.
- Tokens issued for one tenant must not authorize actions in another tenant.
- Deactivated tenants must not authenticate or refresh tokens successfully.
- Cache and object storage prefixes must remain tenant-scoped.

Add integration tests under `tests/test_tenant_isolation.py` when changing
tenant authorization paths.
