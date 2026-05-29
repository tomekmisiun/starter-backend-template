from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import Token, UserCreate, UserLogin, UserRead
from app.services.auth_service import create_user, login_user
from app.api.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    return create_user(db, user_data)


@router.post("/login", response_model=Token)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db),
):
    access_token = login_user(db, login_data)

    return Token(access_token=access_token)

@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user