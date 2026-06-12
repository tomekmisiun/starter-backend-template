import json
import time
from dataclasses import dataclass, fields
from datetime import datetime, timezone

from redis import Redis

from app.core.config import settings
from app.core.ids import uuid7
from app.core.redis import redis_client
from app.core.request_context import get_request_id

MAX_JOB_ERROR_LENGTH = 500


@dataclass(frozen=True)
class Job:
    id: str
    type: str
    payload: dict
    attempts: int = 0
    request_id: str | None = None
    last_error: str | None = None
    failed_at: str | None = None

    def to_json(self) -> str:
        data = {
            "id": self.id,
            "type": self.type,
            "payload": self.payload,
            "attempts": self.attempts,
        }

        if self.request_id is not None:
            data["request_id"] = self.request_id

        if self.last_error is not None:
            data["last_error"] = self.last_error

        if self.failed_at is not None:
            data["failed_at"] = self.failed_at

        return json.dumps(data)

    def to_dict(self) -> dict:
        return {field.name: getattr(self, field.name) for field in fields(self)}

    @classmethod
    def from_json(cls, raw_job: str) -> "Job":
        data = json.loads(raw_job)
        return cls(
            id=data["id"],
            type=data["type"],
            payload=data["payload"],
            attempts=data.get("attempts", 0),
            request_id=data.get("request_id"),
            last_error=data.get("last_error"),
            failed_at=data.get("failed_at"),
        )

    def with_next_attempt(self) -> "Job":
        return Job(
            id=self.id,
            type=self.type,
            payload=self.payload,
            attempts=self.attempts + 1,
            request_id=self.request_id,
            last_error=self.last_error,
            failed_at=self.failed_at,
        )

    def with_error(self, message: str) -> "Job":
        return Job(
            id=self.id,
            type=self.type,
            payload=self.payload,
            attempts=self.attempts,
            request_id=self.request_id,
            last_error=message[:MAX_JOB_ERROR_LENGTH],
            failed_at=self.failed_at,
        )

    def with_failed_at(self, failed_at: str | None = None) -> "Job":
        timestamp = failed_at or datetime.now(timezone.utc).isoformat()

        return Job(
            id=self.id,
            type=self.type,
            payload=self.payload,
            attempts=self.attempts,
            request_id=self.request_id,
            last_error=self.last_error,
            failed_at=timestamp,
        )


def calculate_retry_delay_seconds(attempts: int) -> int:
    if attempts <= 0:
        return settings.worker_retry_backoff_base_seconds

    delay = settings.worker_retry_backoff_base_seconds * (2 ** (attempts - 1))
    return min(delay, settings.worker_retry_backoff_max_seconds)


def enqueue_job(
    job_type: str,
    payload: dict,
    *,
    redis: Redis = redis_client,
    queue_name: str = settings.worker_queue_name,
) -> Job:
    job = Job(
        id=str(uuid7()),
        type=job_type,
        payload=payload,
        request_id=get_request_id(),
    )
    redis.lpush(queue_name, job.to_json())

    return job


def dequeue_job(
    *,
    redis: Redis = redis_client,
    queue_name: str = settings.worker_queue_name,
    processing_queue_name: str = settings.worker_processing_queue_name,
    timeout_seconds: int = settings.worker_poll_timeout_seconds,
) -> Job | None:
    raw_job = redis.brpoplpush(queue_name, processing_queue_name, timeout=timeout_seconds)

    if raw_job is None:
        return None

    return Job.from_json(raw_job)


def ack_job(
    job: Job,
    *,
    redis: Redis = redis_client,
    processing_queue_name: str = settings.worker_processing_queue_name,
) -> None:
    redis.lrem(processing_queue_name, 1, job.to_json())


def schedule_retry(
    job: Job,
    error: Exception | str,
    *,
    redis: Redis = redis_client,
    processing_queue_name: str = settings.worker_processing_queue_name,
    delayed_queue_name: str = settings.worker_delayed_queue_name,
    now: float | None = None,
) -> Job:
    error_message = str(error)
    retried_job = job.with_next_attempt().with_error(error_message)
    current_time = now if now is not None else time.time()
    available_at = current_time + calculate_retry_delay_seconds(retried_job.attempts)

    redis.lrem(processing_queue_name, 1, job.to_json())
    redis.zadd(delayed_queue_name, {retried_job.to_json(): available_at})

    return retried_job


def promote_delayed_jobs(
    *,
    redis: Redis = redis_client,
    queue_name: str = settings.worker_queue_name,
    delayed_queue_name: str = settings.worker_delayed_queue_name,
    now: float | None = None,
) -> int:
    current_time = now if now is not None else time.time()
    raw_jobs = redis.zrangebyscore(delayed_queue_name, 0, current_time)
    promoted_count = 0

    for raw_job in raw_jobs:
        if redis.zrem(delayed_queue_name, raw_job):
            redis.lpush(queue_name, raw_job)
            promoted_count += 1

    return promoted_count


def requeue_job(
    job: Job,
    *,
    redis: Redis = redis_client,
    queue_name: str = settings.worker_queue_name,
) -> Job:
    retried_job = job.with_next_attempt()
    redis.lpush(queue_name, retried_job.to_json())

    return retried_job


def move_job_to_failed_queue(
    job: Job,
    error: Exception | str | None = None,
    *,
    redis: Redis = redis_client,
    processing_queue_name: str = settings.worker_processing_queue_name,
    failed_queue_name: str = settings.worker_failed_queue_name,
) -> Job:
    failed_job = job.with_failed_at()

    if error is not None:
        failed_job = failed_job.with_error(str(error))
    elif job.last_error is not None:
        failed_job = failed_job.with_error(job.last_error)

    redis.lrem(processing_queue_name, 1, job.to_json())
    redis.lpush(failed_queue_name, failed_job.to_json())

    return failed_job


def list_failed_jobs(
    *,
    redis: Redis = redis_client,
    failed_queue_name: str = settings.worker_failed_queue_name,
    limit: int = 20,
) -> list[Job]:
    raw_jobs = redis.lrange(failed_queue_name, 0, limit - 1)

    return [Job.from_json(raw_job) for raw_job in raw_jobs]


def requeue_failed_jobs(
    *,
    redis: Redis = redis_client,
    queue_name: str = settings.worker_queue_name,
    failed_queue_name: str = settings.worker_failed_queue_name,
    limit: int | None = None,
) -> int:
    requeued_count = 0

    while limit is None or requeued_count < limit:
        raw_job = redis.rpop(failed_queue_name)

        if raw_job is None:
            break

        job = Job.from_json(raw_job)
        redis.lpush(queue_name, job.to_json())
        requeued_count += 1

    return requeued_count


def try_acquire_maintenance_lock(
    *,
    redis: Redis = redis_client,
    lock_key: str = settings.worker_maintenance_lock_key,
    ttl_seconds: int = settings.worker_maintenance_lock_ttl_seconds,
) -> bool:
    return redis.set(lock_key, "1", nx=True, ex=ttl_seconds) is True
