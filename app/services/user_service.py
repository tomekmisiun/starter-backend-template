import hashlib
import json

from sqlalchemy.orm import Session

from app.core.cache import delete_cache_pattern, get_json_cache, set_json_cache
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserAdminUpdate, UserRead, UserSelfUpdate
from app.services.tenant_service import build_tenant_cache_prefix


USERS_LIST_CACHE_PREFIX = "users:list:v1"


def get_users(
    db: Session,
    tenant_id: int,
    skip: int,
    limit: int,
    sort_by: str = "id",
    sort_order: str = "asc",
    role: str | None = None,
    is_active: bool | None = None,
    search=None,
):
    cache_key = build_users_list_cache_key(
        tenant_id=tenant_id,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
        role=role,
        is_active=is_active,
        search=search,
    )

    if settings.users_cache_enabled:
        cached_users = get_json_cache(cache_key)

        if cached_users is not None:
            return cached_users

    allowed_sort_fields = {
        "id": User.id,
        "email": User.email,
        "role": User.role,
        "is_active": User.is_active,
    }

    query = db.query(User).filter(User.tenant_id == tenant_id)

    if role is not None:
        query = query.filter(User.role == role)

    if is_active is None:
        query = query.filter(User.is_active.is_(True))
    else:
        query = query.filter(User.is_active == is_active)

    sort_column = allowed_sort_fields.get(sort_by, User.id)

    if sort_order == "desc":
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()

    if search is not None:
        query = query.filter(User.email.ilike(f"%{search}%"))

    users = (
        query
        .order_by(sort_column)
        .offset(skip)
        .limit(limit)
        .all()
    )

    if settings.users_cache_enabled:
        set_json_cache(
            cache_key,
            [
                UserRead.model_validate(user).model_dump(mode="json")
                for user in users
            ],
            ttl_seconds=settings.users_cache_ttl_seconds,
        )

    return users


def build_users_list_cache_key(
    *,
    tenant_id: int,
    skip: int,
    limit: int,
    sort_by: str,
    sort_order: str,
    role: str | None,
    is_active: bool | None,
    search: str | None,
) -> str:
    cache_params = {
        "skip": skip,
        "limit": limit,
        "sort_by": sort_by,
        "sort_order": sort_order,
        "role": role,
        "is_active": is_active,
        "search": search,
    }
    cache_hash = hashlib.sha256(
        json.dumps(cache_params, sort_keys=True).encode("utf-8")
    ).hexdigest()

    return f"{build_tenant_cache_prefix(tenant_id)}:{USERS_LIST_CACHE_PREFIX}:{cache_hash}"


def invalidate_users_list_cache(tenant_id: int) -> None:
    delete_cache_pattern(
        f"{build_tenant_cache_prefix(tenant_id)}:{USERS_LIST_CACHE_PREFIX}:*"
    )


def increment_user_token_version(db: Session, user: User) -> User:
    user.token_version += 1
    db.commit()
    db.refresh(user)
    invalidate_users_list_cache(user.tenant_id)
    return user


def get_user_by_id(db: Session, user_id: int, tenant_id: int) -> User | None:
    return (
        db.query(User)
        .filter(User.id == user_id, User.tenant_id == tenant_id)
        .first()
    )


def update_user(
    db: Session,
    user: User,
    user_update: UserAdminUpdate | UserSelfUpdate,
    *,
    commit: bool = True,
) -> User:
    update_data = user_update.model_dump(exclude_unset=True)
    should_invalidate_tokens = (
        "role" in update_data and update_data["role"] != user.role
    )

    for field, value in update_data.items():
        setattr(user, field, value)

    if should_invalidate_tokens:
        user.token_version += 1

    if commit:
        db.commit()
        db.refresh(user)
        invalidate_users_list_cache(user.tenant_id)
    else:
        db.flush()

    return user


def delete_user(db: Session, user: User, *, commit: bool = True) -> None:
    tenant_id = user.tenant_id
    db.delete(user)

    if commit:
        db.commit()
        invalidate_users_list_cache(tenant_id)
    else:
        db.flush()


def deactivate_user(
    db: Session,
    user_id: int,
    tenant_id: int,
    *,
    commit: bool = True,
) -> User | None:
    user = get_user_by_id(db, user_id, tenant_id)

    if not user:
        return None

    user.is_active = False
    user.token_version += 1

    if commit:
        db.commit()
        db.refresh(user)
        invalidate_users_list_cache(tenant_id)
    else:
        db.flush()

    return user


def activate_user(
    db: Session,
    user_id: int,
    tenant_id: int,
    *,
    commit: bool = True,
) -> User | None:
    user = get_user_by_id(db, user_id, tenant_id)

    if not user:
        return None

    user.is_active = True

    if commit:
        db.commit()
        db.refresh(user)
        invalidate_users_list_cache(tenant_id)
    else:
        db.flush()

    return user
