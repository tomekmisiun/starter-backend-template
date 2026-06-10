from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    LogoutRequest,
    MessageResponse,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshTokenRequest,
    Token,
    UserCreate,
    UserLogin,
    UserRead,
)
from app.services.auth_service import (
    create_user,
    login_user,
    logout_user,
    rotate_refresh_token,
)
from app.services.password_reset_service import (
    confirm_password_reset,
    request_password_reset,
)

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
    access_token, refresh_token = login_user(db, login_data)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/refresh", response_model=Token)
def refresh_token(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    access_token, refresh_token = rotate_refresh_token(db, token_data.refresh_token)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(token_data: LogoutRequest):
    logout_user(token_data.refresh_token)


@router.post("/password-reset/request", response_model=MessageResponse)
def request_reset_password(
    reset_request: PasswordResetRequest,
    db: Session = Depends(get_db),
):
    message = request_password_reset(db, reset_request)

    return MessageResponse(message=message)


@router.post("/password-reset/confirm", response_model=MessageResponse)
def confirm_reset_password(
    reset_confirm: PasswordResetConfirm,
    db: Session = Depends(get_db),
):
    message = confirm_password_reset(db, reset_confirm)

    return MessageResponse(message=message)
