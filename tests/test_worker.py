from app.core.job_queue import (
    Job,
    dequeue_job,
    enqueue_job,
    list_failed_jobs,
    move_job_to_failed_queue,
    requeue_failed_jobs,
)
from app.worker import process_next_job, run_scheduled_maintenance


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

    def lrange(self, queue_name: str, start: int, end: int):
        queue = self.queues.get(queue_name, [])
        stop = end + 1 if end >= 0 else None

        return queue[start:stop]

    def rpop(self, queue_name: str):
        queue = self.queues.get(queue_name, [])

        if not queue:
            return None

        return queue.pop()


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


def test_list_failed_jobs_returns_failed_queue_items():
    redis = FakeRedis()
    job = Job(
        id="job-id",
        type="send_password_reset_email",
        payload={"user_id": 123},
        attempts=3,
    )

    move_job_to_failed_queue(
        job,
        redis=redis,
        failed_queue_name="test_failed_jobs",
    )

    failed_jobs = list_failed_jobs(
        redis=redis,
        failed_queue_name="test_failed_jobs",
    )

    assert failed_jobs == [job]


def test_requeue_failed_jobs_moves_jobs_back_to_main_queue():
    redis = FakeRedis()
    job = Job(
        id="job-id",
        type="send_password_reset_email",
        payload={"user_id": 123},
        attempts=3,
    )

    move_job_to_failed_queue(
        job,
        redis=redis,
        failed_queue_name="test_failed_jobs",
    )

    requeued_count = requeue_failed_jobs(
        redis=redis,
        queue_name="test_jobs",
        failed_queue_name="test_failed_jobs",
    )

    dequeued_job = dequeue_job(
        redis=redis,
        queue_name="test_jobs",
        timeout_seconds=1,
    )

    assert requeued_count == 1
    assert dequeued_job == job


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


def test_scheduled_maintenance_runs_when_due(monkeypatch):
    cleanup_calls = []

    class FakeSession:
        def close(self):
            pass

    monkeypatch.setattr("app.worker.last_maintenance_run_at", None)
    monkeypatch.setattr("app.worker.settings.worker_maintenance_enabled", True)
    monkeypatch.setattr(
        "app.worker.settings.worker_maintenance_interval_seconds",
        60,
    )
    monkeypatch.setattr("app.worker.SessionLocal", lambda: FakeSession())
    monkeypatch.setattr(
        "app.worker.cleanup_expired_password_reset_tokens",
        lambda db: cleanup_calls.append(db) or 2,
    )

    did_run = run_scheduled_maintenance(now=100)

    assert did_run is True
    assert len(cleanup_calls) == 1


def test_scheduled_maintenance_skips_until_interval(monkeypatch):
    cleanup_calls = []

    monkeypatch.setattr("app.worker.last_maintenance_run_at", 100)
    monkeypatch.setattr("app.worker.settings.worker_maintenance_enabled", True)
    monkeypatch.setattr(
        "app.worker.settings.worker_maintenance_interval_seconds",
        60,
    )
    monkeypatch.setattr(
        "app.worker.cleanup_expired_password_reset_tokens",
        lambda db: cleanup_calls.append(db),
    )

    did_run = run_scheduled_maintenance(now=120)

    assert did_run is False
    assert cleanup_calls == []


def test_scheduled_maintenance_can_be_disabled(monkeypatch):
    cleanup_calls = []

    monkeypatch.setattr("app.worker.settings.worker_maintenance_enabled", False)
    monkeypatch.setattr(
        "app.worker.cleanup_expired_password_reset_tokens",
        lambda db: cleanup_calls.append(db),
    )

    did_run = run_scheduled_maintenance(now=100)

    assert did_run is False
    assert cleanup_calls == []
