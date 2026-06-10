def test_metrics_endpoint_exposes_prometheus_text(client):
    response = client.get("/metrics")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "# HELP http_requests_total" in response.text
    assert "# TYPE http_request_duration_seconds histogram" in response.text
    assert 'app_info{service="starter-backend-template"} 1' in response.text


def test_metrics_record_requests(client):
    client.get("/health")

    response = client.get("/metrics")

    assert response.status_code == 200
    assert 'http_requests_total{method="GET",path="/health",status_code="200"}' in (
        response.text
    )
    assert 'http_request_duration_seconds_count{method="GET",path="/health",' in (
        response.text
    )


def test_metrics_use_route_templates_instead_of_raw_paths(client):
    client.get("/users/123")

    response = client.get("/metrics")

    assert 'path="/users/{user_id}"' in response.text
    assert 'path="/users/123"' not in response.text


def test_metrics_endpoint_does_not_record_itself(client):
    client.get("/metrics")
    response = client.get("/metrics")

    assert 'path="/metrics"' not in response.text
