from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserAdminUpdate, UserSelfUpdate


def get_users(
    db: Session,
    skip: int,
    limit: int,
    sort_by: str = "id",
    sort_order: str = "asc",
    role: str | None = None,
    is_active: bool | None = None,
    search=None,
):
    allowed_sort_fields = {
        "id": User.id,
        "email": User.email,
        "role": User.role,
        "is_active": User.is_active,
    }

    query = db.query(User)

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

    return (
        query
        .order_by(sort_column)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def update_user(
    db: Session,
    user: User,
    user_update: UserAdminUpdate | UserSelfUpdate,
) -> User:
    update_data = user_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()


def deactivate_user(db: Session, user_id: int) -> User | None:
    user = get_user_by_id(db, user_id)

    if not user:
        return None

    user.is_active = False
    db.commit()
    db.refresh(user)

    return user


def activate_user(db: Session, user_id: int) -> User | None:
    user = get_user_by_id(db, user_id)

    if not user:
        return None

    user.is_active = True
    db.commit()
    db.refresh(user)

    return user
