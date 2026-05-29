def test_register(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["is_active"] is True


def test_register_duplicate_email(client):
    payload = {
        "email": "test@example.com",
        "password": "password123",
    }

    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)

    assert response.status_code == 400


def test_login(client):
    client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_me(client):
    client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["is_active"] is True


def test_me_unauthorized(client):
    response = client.get("/auth/me")

    assert response.status_code == 401