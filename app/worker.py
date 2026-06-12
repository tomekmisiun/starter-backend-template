import logging

from app.core.config import settings
from app.core.job_queue import (
    Job,
    ack_job,
    calculate_retry_delay_seconds,
    dequeue_job,
    move_job_to_failed_queue,
    promote_delayed_jobs,
    schedule_retry,
    try_acquire_maintenance_lock,
)
from app.core.log_helpers import job_log_extra
from app.core.logging import configure_logging
from app.db.session import SessionLocal
from app.services.password_reset_service import (
    SEND_PASSWORD_RESET_EMAIL_JOB,
    cleanup_expired_password_reset_tokens,
    create_password_reset_token_and_send_email,
)


logger = logging.getLogger("app.worker")


def handle_job(job: Job) -> None:
    if job.type == SEND_PASSWORD_RESET_EMAIL_JOB:
        user_id = job.payload["user_id"]

        db = SessionLocal()
        try:
            create_password_reset_token_and_send_email(db, user_id)
        finally:
            db.close()

        return

    logger.warning("worker_unknown_job_type", extra=job_log_extra(job))


def process_next_job() -> bool:
    promote_delayed_jobs()
    job = dequeue_job()

    if job is None:
        return False

    logger.info(
        "worker_job_started",
        extra={**job_log_extra(job), "attempts": job.attempts},
    )

    try:
        handle_job(job)
    except Exception as exc:
        if job.attempts < settings.worker_max_retries:
            retried_job = schedule_retry(job, exc)
            logger.exception(
                "worker_job_scheduled_for_retry",
                extra={
                    **job_log_extra(retried_job),
                    "attempts": retried_job.attempts,
                    "retry_delay_seconds": calculate_retry_delay_seconds(
                        retried_job.attempts
                    ),
                },
            )
            return True

        failed_job = move_job_to_failed_queue(job, exc)
        logger.exception(
            "worker_job_failed",
            extra={**job_log_extra(failed_job), "attempts": failed_job.attempts},
        )
        return True

    ack_job(job)
    logger.info("worker_job_completed", extra=job_log_extra(job))
    return True


def run_scheduled_maintenance(now: float | None = None) -> bool:
    del now

    if not settings.worker_maintenance_enabled:
        return False

    if not try_acquire_maintenance_lock(
        ttl_seconds=settings.worker_maintenance_interval_seconds,
    ):
        return False

    db = SessionLocal()

    try:
        deleted_count = cleanup_expired_password_reset_tokens(db)
    finally:
        db.close()

    logger.info(
        "worker_maintenance_completed expired_password_reset_tokens_deleted=%s",
        deleted_count,
    )

    return True


def run_worker() -> None:
    configure_logging()
    logger.info("worker_started queue=%s", settings.worker_queue_name)

    while True:
        run_scheduled_maintenance()
        process_next_job()


if __name__ == "__main__":
    run_worker()
