import json
from dataclasses import dataclass
from uuid import uuid4

from redis import Redis

from app.core.config import settings
from app.core.redis import redis_client


@dataclass(frozen=True)
class Job:
    id: str
    type: str
    payload: dict
    attempts: int = 0

    def to_json(self) -> str:
        return json.dumps(
            {
                "id": self.id,
                "type": self.type,
                "payload": self.payload,
                "attempts": self.attempts,
            }
        )

    @classmethod
    def from_json(cls, raw_job: str) -> "Job":
        data = json.loads(raw_job)
        return cls(
            id=data["id"],
            type=data["type"],
            payload=data["payload"],
            attempts=data.get("attempts", 0),
        )

    def with_next_attempt(self) -> "Job":
        return Job(
            id=self.id,
            type=self.type,
            payload=self.payload,
            attempts=self.attempts + 1,
        )


def enqueue_job(
    job_type: str,
    payload: dict,
    *,
    redis: Redis = redis_client,
    queue_name: str = settings.worker_queue_name,
) -> Job:
    job = Job(
        id=str(uuid4()),
        type=job_type,
        payload=payload,
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
