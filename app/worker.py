import logging
import time

from app.core.config import settings
from app.core.job_queue import (
    Job,
    dequeue_job,
    move_job_to_failed_queue,
    requeue_job,
)
from app.core.logging import configure_logging
from app.db.session import SessionLocal
from app.services.password_reset_service import (
    SEND_PASSWORD_RESET_EMAIL_JOB,
    cleanup_expired_password_reset_tokens,
    create_password_reset_token_and_send_email,
)


logger = logging.getLogger("app.worker")
last_maintenance_run_at: float | None = None


def handle_job(job: Job) -> None:
    if job.type == SEND_PASSWORD_RESET_EMAIL_JOB:
        user_id = job.payload["user_id"]

        db = SessionLocal()
        try:
            create_password_reset_token_and_send_email(db, user_id)
        finally:
            db.close()

        return

    logger.warning("worker_unknown_job_type job_id=%s job_type=%s", job.id, job.type)


def process_next_job() -> bool:
    job = dequeue_job()

    if job is None:
        return False

    logger.info(
        "worker_job_started job_id=%s job_type=%s attempts=%s",
        job.id,
        job.type,
        job.attempts,
    )

    try:
        handle_job(job)
    except Exception:
        if job.attempts < settings.worker_max_retries:
            retried_job = requeue_job(job)
            logger.exception(
                "worker_job_requeued job_id=%s job_type=%s attempts=%s",
                retried_job.id,
                retried_job.type,
                retried_job.attempts,
            )
            return True

        move_job_to_failed_queue(job)
        logger.exception(
            "worker_job_failed job_id=%s job_type=%s attempts=%s",
            job.id,
            job.type,
            job.attempts,
        )
        return True

    logger.info("worker_job_completed job_id=%s job_type=%s", job.id, job.type)
    return True


def run_scheduled_maintenance(now: float | None = None) -> bool:
    global last_maintenance_run_at

    if not settings.worker_maintenance_enabled:
        return False

    current_time = now if now is not None else time.monotonic()

    if (
        last_maintenance_run_at is not None
        and current_time - last_maintenance_run_at
        < settings.worker_maintenance_interval_seconds
    ):
        return False

    last_maintenance_run_at = current_time
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
