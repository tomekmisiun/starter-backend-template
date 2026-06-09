from uuid import UUID


def test_request_id_header_is_added(client):
    response = client.get("/health")

    assert response.status_code == 200

    request_id = response.headers["X-Request-ID"]
    UUID(request_id)


def test_request_id_header_is_preserved(client):
    request_id = "test-request-id"

    response = client.get(
        "/health",
        headers={"X-Request-ID": request_id},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == request_id


def test_process_time_header_is_added(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert float(response.headers["X-Process-Time"]) >= 0
