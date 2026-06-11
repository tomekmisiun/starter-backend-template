from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.api.dependencies.rate_limit import password_reset_rate_limit
from app.api.dependencies.auth import get_current_user
from app.api.openapi import AUTH_ERROR_RESPONSES, RATE_LIMITED_ERROR_RESPONSES
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


@router.post(
    "/register",
    response_model=UserRead,
    summary="Register a new user",
    description="Create an active user account with the default `user` role.",
    responses=AUTH_ERROR_RESPONSES,
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    return create_user(db, user_data)


@router.post(
    "/login",
    response_model=Token,
    summary="Login and receive JWT tokens",
    description=(
        "Authenticate with email and password. Returns a short-lived access "
        "token and a refresh token used for rotation."
    ),
    responses=AUTH_ERROR_RESPONSES,
)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db),
):
    access_token, refresh_token = login_user(db, login_data)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get the current user profile",
    responses=AUTH_ERROR_RESPONSES,
)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post(
    "/refresh",
    response_model=Token,
    summary="Rotate access and refresh tokens",
    description="Exchange a valid refresh token for a new access/refresh pair.",
    responses=AUTH_ERROR_RESPONSES,
)
def refresh_token(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    access_token, refresh_token = rotate_refresh_token(db, token_data.refresh_token)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout and revoke refresh token",
    description="Revokes the submitted refresh token in Redis.",
    responses=AUTH_ERROR_RESPONSES,
)
def logout(token_data: LogoutRequest):
    logout_user(token_data.refresh_token)


@router.post(
    "/password-reset/request",
    response_model=MessageResponse,
    summary="Request a password reset email",
    description=(
        "Always returns the same success message to avoid account enumeration. "
        "Active users receive a background email job with a single-use reset "
        "token."
    ),
    responses=RATE_LIMITED_ERROR_RESPONSES,
)
async def request_reset_password(
    request: Request,
    reset_request: PasswordResetRequest,
    db: Session = Depends(get_db),
):
    request.scope["_json"] = {"email": str(reset_request.email)}
    password_reset_rate_limit(request)
    message = request_password_reset(db, reset_request)

    return MessageResponse(message=message)


@router.post(
    "/password-reset/confirm",
    response_model=MessageResponse,
    summary="Confirm a password reset",
    description="Set a new password using a valid, unused, unexpired reset token.",
    responses=AUTH_ERROR_RESPONSES,
)
def confirm_reset_password(
    reset_confirm: PasswordResetConfirm,
    db: Session = Depends(get_db),
):
    message = confirm_password_reset(db, reset_confirm)

    return MessageResponse(message=message)
