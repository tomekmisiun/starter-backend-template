from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user, require_role
from app.api.openapi import ADMIN_ERROR_RESPONSES, PROTECTED_ERROR_RESPONSES
from app.db.session import get_db
from app.models.audit_log import AuditAction
from app.models.user import User
from app.schemas.user import UserAdminUpdate, UserRead, UserSelfUpdate
from app.services.audit_log_service import create_audit_log
from app.services.user_service import (
    activate_user,
    deactivate_user,
    delete_user,
    get_user_by_id,
    get_users,
    update_user,
)


class UserSortBy(str, Enum):
    id = "id"
    email = "email"
    role = "role"
    is_active = "is_active"


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class UserRole(str, Enum):
    admin = "admin"
    user = "user"


router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    response_model=list[UserRead],
    summary="List users",
    description="Admin-only paginated user listing with sorting, filters, and search.",
    responses=ADMIN_ERROR_RESPONSES,
)
def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    sort_by: UserSortBy = Query(UserSortBy.id),
    sort_order: SortOrder = Query(SortOrder.asc),
    role: UserRole | None = None,
    is_active: bool | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    skip = (page - 1) * size

    return get_users(
        db=db,
        skip=skip,
        limit=size,
        sort_by=sort_by.value,
        sort_order=sort_order.value,
        role=role.value if role else None,
        is_active=is_active,
        search=search,
    )


@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="Get a user by ID",
    description="Admins can read any user. Regular users can only read themselves.",
    responses=PROTECTED_ERROR_RESPONSES,
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    return user


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    summary="Update a user",
    description=(
        "Admins can update managed fields and activation state. Regular users "
        "can update only their own safe profile fields."
    ),
    responses=PROTECTED_ERROR_RESPONSES,
)
def patch_user(
    user_id: int,
    user_update: UserAdminUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    if current_user.role == "admin":
        update_data = user_update
    else:
        update_data = UserSelfUpdate(**user_update.model_dump(exclude_unset=True))

    updated_user = update_user(db, user, update_data)

    if current_user.role == "admin":
        create_audit_log(
            db=db,
            admin_id=current_user.id,
            action=AuditAction.USER_UPDATED,
            target_user_id=user_id,
        )

    return updated_user


@router.patch(
    "/{user_id}/deactivate",
    response_model=UserRead,
    summary="Deactivate a user",
    responses=ADMIN_ERROR_RESPONSES,
)
def deactivate_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    user = deactivate_user(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    create_audit_log(
        db=db,
        admin_id=current_user.id,
        action=AuditAction.USER_DEACTIVATED,
        target_user_id=user_id,
    )

    return user


@router.patch(
    "/{user_id}/activate",
    response_model=UserRead,
    summary="Activate a user",
    responses=ADMIN_ERROR_RESPONSES,
)
def activate_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    user = activate_user(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    create_audit_log(
        db=db,
        admin_id=current_user.id,
        action=AuditAction.USER_ACTIVATED,
        target_user_id=user_id,
    )

    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
    responses=ADMIN_ERROR_RESPONSES,
)
def remove_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    user = get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    delete_user(db, user)
    create_audit_log(
        db=db,
        admin_id=current_user.id,
        action=AuditAction.USER_DELETED,
        target_user_id=user_id,
    )
