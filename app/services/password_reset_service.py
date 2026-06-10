import logging
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.job_queue import enqueue_job
from app.core.config import settings
from app.core.security import (
    generate_password_reset_token,
    hash_password,
    hash_password_reset_token,
)
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User
from app.schemas.auth import PasswordResetConfirm, PasswordResetRequest
from app.services.auth_service import get_user_by_email
from app.services.email_service import EmailDeliveryError, get_email_service


logger = logging.getLogger("app.password_reset")

SEND_PASSWORD_RESET_EMAIL_JOB = "send_password_reset_email"
PASSWORD_RESET_RESPONSE_MESSAGE = (
    "If an account exists for this email, password reset instructions were sent."
)
INVALID_RESET_TOKEN_MESSAGE = "Invalid or expired password reset token"


def request_password_reset(db: Session, reset_request: PasswordResetRequest) -> str:
    user = get_user_by_email(db, str(reset_request.email))

    if user is None or not user.is_active:
        logger.info("password_reset_request_ignored")
        return PASSWORD_RESET_RESPONSE_MESSAGE

    job = enqueue_password_reset_email_job(user.id)
    logger.info(
        "password_reset_email_job_enqueued user_id=%s job_id=%s",
        user.id,
        job.id,
    )

    return PASSWORD_RESET_RESPONSE_MESSAGE


def enqueue_password_reset_email_job(user_id: int):
    return enqueue_job(
        SEND_PASSWORD_RESET_EMAIL_JOB,
        {"user_id": user_id},
    )


def create_password_reset_token_and_send_email(db: Session, user_id: int) -> None:
    user = db.query(User).filter(User.id == user_id).first()

    if user is None or not user.is_active:
        logger.info(
            "password_reset_email_job_skipped reason=inactive_or_missing_user user_id=%s",
            user_id,
        )
        return

    raw_token = generate_password_reset_token()
    token_hash = hash_password_reset_token(raw_token)
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.password_reset_token_expire_minutes
    )

    reset_token = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    db.add(reset_token)
    db.flush()

    logger.info(
        "password_reset_token_created user_id=%s token_id=%s expires_at=%s",
        user.id,
        reset_token.id,
        expires_at.isoformat(),
    )

    try:
        get_email_service().send_password_reset_email(user.email, raw_token)
    except EmailDeliveryError:
        db.rollback()
        logger.exception(
            "password_reset_email_delivery_failed user_id=%s token_id=%s",
            user.id,
            reset_token.id,
        )
        raise

    db.commit()
    logger.info(
        "password_reset_email_job_completed user_id=%s token_id=%s",
        user.id,
        reset_token.id,
    )


def confirm_password_reset(db: Session, reset_confirm: PasswordResetConfirm) -> str:
    token_hash = hash_password_reset_token(reset_confirm.token)
    reset_token = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.token_hash == token_hash)
        .first()
    )

    if reset_token is None:
        logger.warning("password_reset_confirm_rejected reason=invalid_token")
        raise_invalid_reset_token()

    now = datetime.now(timezone.utc)

    if reset_token.used_at is not None:
        logger.warning(
            "password_reset_confirm_rejected reason=used token_id=%s",
            reset_token.id,
        )
        raise_invalid_reset_token()

    if reset_token.expires_at < now:
        logger.warning(
            "password_reset_confirm_rejected reason=expired token_id=%s",
            reset_token.id,
        )
        raise_invalid_reset_token()

    user = db.query(User).filter(User.id == reset_token.user_id).first()

    if user is None or not user.is_active:
        logger.warning(
            "password_reset_confirm_rejected reason=inactive_or_missing_user token_id=%s",
            reset_token.id,
        )
        raise_invalid_reset_token()

    user.hashed_password = hash_password(reset_confirm.new_password)
    (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used_at.is_(None),
        )
        .update({"used_at": now}, synchronize_session=False)
    )
    db.commit()

    logger.info(
        "password_reset_confirmed user_id=%s token_id=%s",
        user.id,
        reset_token.id,
    )

    return "Password has been reset."


def raise_invalid_reset_token() -> None:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=INVALID_RESET_TOKEN_MESSAGE,
    )
