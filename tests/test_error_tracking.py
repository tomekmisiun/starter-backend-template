from app.core.config import Settings
from app.core.error_tracking import initialize_error_tracking


def test_initialize_error_tracking_is_disabled_without_dsn(monkeypatch):
    def fail_init(**kwargs):
        raise AssertionError("sentry_sdk.init should not be called without a DSN")

    monkeypatch.setattr("app.core.error_tracking.sentry_sdk.init", fail_init)

    initialized = initialize_error_tracking(
        Settings(
            _env_file=None,
            secret_key="development-secret",
        )
    )

    assert initialized is False


def test_initialize_error_tracking_calls_sentry_with_config(monkeypatch):
    init_calls = []

    def fake_init(**kwargs):
        init_calls.append(kwargs)

    monkeypatch.setattr("app.core.error_tracking.sentry_sdk.init", fake_init)

    initialized = initialize_error_tracking(
        Settings(
            _env_file=None,
            environment="staging",
            secret_key="staging-secret",
            sentry_dsn="https://public@example.ingest.sentry.io/1",
            sentry_traces_sample_rate=0.25,
            sentry_send_default_pii=True,
            sentry_release="template@1.2.3",
        )
    )

    assert initialized is True
    assert init_calls == [
        {
            "dsn": "https://public@example.ingest.sentry.io/1",
            "environment": "staging",
            "traces_sample_rate": 0.25,
            "send_default_pii": True,
            "release": "template@1.2.3",
        }
    ]
