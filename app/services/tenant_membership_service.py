from fastapi import HTTPException, status

from app.models.tenant import Tenant
from app.models.user import User


def user_belongs_to_tenant(user: User, tenant_id: int) -> bool:
    return user.tenant_id == tenant_id


def assert_user_belongs_to_tenant(user: User, tenant_id: int) -> None:
    if not user_belongs_to_tenant(user, tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant access denied",
        )


def assert_active_tenant_membership(user: User) -> None:
    tenant = user.tenant

    if tenant is None or not tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant access denied",
        )


def assert_request_tenant_matches_user(user: User, request_tenant: Tenant) -> None:
    if user.tenant_id != request_tenant.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant access denied",
        )
