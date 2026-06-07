from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserUpdate


def get_users(
    db: Session,
    skip: int,
    limit: int,
    sort_by: str = "id",
    sort_order: str = "asc",
):
    allowed_sort_fields = {
        "id": User.id,
        "email": User.email,
        "role": User.role,
        "is_active": User.is_active,
    }

    sort_column = allowed_sort_fields.get(sort_by, User.id)

    if sort_order == "desc":
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()

    return (
        db.query(User)
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
    user_update: UserUpdate,
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