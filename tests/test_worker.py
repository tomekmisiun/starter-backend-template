from app.core.job_queue import Job, dequeue_job, enqueue_job
from app.worker import process_next_job


class FakeRedis:
    def __init__(self):
        self.queues = {}

    def lpush(self, queue_name: str, value: str) -> None:
        self.queues.setdefault(queue_name, []).insert(0, value)

    def brpop(self, queue_name: str, timeout: int):
        queue = self.queues.get(queue_name, [])

        if not queue:
            return None

        return queue_name, queue.pop()


def test_enqueue_and_dequeue_job_round_trip():
    redis = FakeRedis()

    enqueued_job = enqueue_job(
        "send_password_reset_email",
        {"user_id": 123},
        redis=redis,
        queue_name="test_jobs",
    )
    dequeued_job = dequeue_job(
        redis=redis,
        queue_name="test_jobs",
        timeout_seconds=1,
    )

    assert dequeued_job == enqueued_job


def test_dequeue_job_returns_none_when_queue_is_empty():
    redis = FakeRedis()

    dequeued_job = dequeue_job(
        redis=redis,
        queue_name="test_jobs",
        timeout_seconds=1,
    )

    assert dequeued_job is None


def test_process_next_job_requeues_failed_job(monkeypatch):
    job = Job(
        id="job-id",
        type="send_password_reset_email",
        payload={"user_id": 1},
        attempts=0,
    )
    requeued_jobs = []
    failed_jobs = []

    monkeypatch.setattr("app.worker.dequeue_job", lambda: job)
    monkeypatch.setattr(
        "app.worker.handle_job",
        lambda queued_job: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    monkeypatch.setattr(
        "app.worker.requeue_job",
        lambda failed_job: requeued_jobs.append(failed_job.with_next_attempt())
        or failed_job.with_next_attempt(),
    )
    monkeypatch.setattr(
        "app.worker.move_job_to_failed_queue",
        lambda failed_job: failed_jobs.append(failed_job),
    )

    processed = process_next_job()

    assert processed is True
    assert requeued_jobs[0].attempts == 1
    assert failed_jobs == []


def test_process_next_job_moves_job_to_failed_queue_after_max_retries(monkeypatch):
    job = Job(
        id="job-id",
        type="send_password_reset_email",
        payload={"user_id": 1},
        attempts=3,
    )
    requeued_jobs = []
    failed_jobs = []

    monkeypatch.setattr("app.worker.dequeue_job", lambda: job)
    monkeypatch.setattr(
        "app.worker.handle_job",
        lambda queued_job: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    monkeypatch.setattr(
        "app.worker.requeue_job",
        lambda failed_job: requeued_jobs.append(failed_job.with_next_attempt()),
    )
    monkeypatch.setattr(
        "app.worker.move_job_to_failed_queue",
        lambda failed_job: failed_jobs.append(failed_job),
    )

    processed = process_next_job()

    assert processed is True
    assert requeued_jobs == []
    assert failed_jobs == [job]


def test_process_next_job_returns_false_without_job(monkeypatch):
    monkeypatch.setattr("app.worker.dequeue_job", lambda: None)

    processed = process_next_job()

    assert processed is False
