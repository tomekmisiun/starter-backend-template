import json

from app.core.ids import uuid7
from app.core.webhook_security import compute_hmac_signature


WEBHOOK_PATH = "/api/v1/webhooks/inbound"
WEBHOOK_SECRET = "test-webhook-secret"


def build_webhook_payload(event_id: str | None = None):
    return {
        "provider": "payments",
        "event_id": event_id or f"evt_{uuid7().hex}",
        "event_type": "payment.succeeded",
        "payload": {"amount": 1000, "currency": "usd"},
    }


def build_webhook_headers(raw_body: bytes, idempotency_key: str = "key-1"):
    signature = compute_hmac_signature(raw_body, WEBHOOK_SECRET)

    return {
        "Idempotency-Key": idempotency_key,
        "X-Webhook-Signature": signature,
        "Content-Type": "application/json",
    }


def test_inbound_webhook_requires_signature(client, monkeypatch):
    monkeypatch.setattr(
        "app.core.config.settings.webhook_signature_secret",
        WEBHOOK_SECRET,
    )
    raw_body = json.dumps(build_webhook_payload()).encode("utf-8")

    response = client.post(
        WEBHOOK_PATH,
        content=raw_body,
        headers={"Idempotency-Key": "key-1", "Content-Type": "application/json"},
    )

    assert response.status_code == 401


def test_inbound_webhook_accepts_signed_event(client, monkeypatch):
    monkeypatch.setattr(
        "app.core.config.settings.webhook_signature_secret",
        WEBHOOK_SECRET,
    )
    payload = build_webhook_payload()
    raw_body = json.dumps(payload).encode("utf-8")

    response = client.post(
        WEBHOOK_PATH,
        content=raw_body,
        headers=build_webhook_headers(raw_body),
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "accepted",
        "provider": "payments",
        "event_id": payload["event_id"],
    }


def test_inbound_webhook_rejects_replayed_event_id(client, monkeypatch):
    monkeypatch.setattr(
        "app.core.config.settings.webhook_signature_secret",
        WEBHOOK_SECRET,
    )
    payload = build_webhook_payload()
    raw_body = json.dumps(payload).encode("utf-8")
    headers = build_webhook_headers(raw_body, idempotency_key="key-2")

    first_response = client.post(WEBHOOK_PATH, content=raw_body, headers=headers)
    second_response = client.post(
        WEBHOOK_PATH,
        content=raw_body,
        headers=build_webhook_headers(raw_body, idempotency_key="key-3"),
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 409
    assert second_response.json()["status"] == "duplicate"


def test_inbound_webhook_returns_cached_response_for_same_idempotency_key(
    client,
    monkeypatch,
):
    monkeypatch.setattr(
        "app.core.config.settings.webhook_signature_secret",
        WEBHOOK_SECRET,
    )
    payload = build_webhook_payload()
    raw_body = json.dumps(payload).encode("utf-8")
    headers = build_webhook_headers(raw_body, idempotency_key="key-cache")

    first_response = client.post(WEBHOOK_PATH, content=raw_body, headers=headers)
    second_response = client.post(WEBHOOK_PATH, content=raw_body, headers=headers)

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert second_response.json() == first_response.json()
