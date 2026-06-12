import json
from dataclasses import dataclass

from redis import Redis

from app.core.config import settings
from app.core.ids import uuid7
from app.core.redis import redis_client
from app.core.request_context import get_request_id


@dataclass(frozen=True)
class Job:
    id: str
    type: str
    payload: dict
    attempts: int = 0
    request_id: str | None = None

    def to_json(self) -> str:
        data = {
            "id": self.id,
            "type": self.type,
            "payload": self.payload,
            "attempts": self.attempts,
        }

        if self.request_id is not None:
            data["request_id"] = self.request_id

        return json.dumps(data)

    @classmethod
    def from_json(cls, raw_job: str) -> "Job":
        data = json.loads(raw_job)
        return cls(
            id=data["id"],
            type=data["type"],
            payload=data["payload"],
            attempts=data.get("attempts", 0),
            request_id=data.get("request_id"),
        )

    def with_next_attempt(self) -> "Job":
        return Job(
            id=self.id,
            type=self.type,
            payload=self.payload,
            attempts=self.attempts + 1,
            request_id=self.request_id,
        )


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
    timeout_seconds: int = settings.worker_poll_timeout_seconds,
) -> Job | None:
    result = redis.brpop(queue_name, timeout=timeout_seconds)

    if result is None:
        return None

    _, raw_job = result
    return Job.from_json(raw_job)


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
    *,
    redis: Redis = redis_client,
    failed_queue_name: str = settings.worker_failed_queue_name,
) -> None:
    redis.lpush(failed_queue_name, job.to_json())


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
