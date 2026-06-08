from app.models.user import User


def deactivate_user_by_email(db, email: str) -> None:
    user = db.query(User).filter(User.email == email).first()
    user.is_active = False
    db.commit()


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


def test_refresh_token(client):
    register_data = {
        "email": "test@example.com",
        "password": "password123",
    }

    client.post("/auth/register", json=register_data)

    login_response = client.post(
        "/auth/login",
        json=register_data,
    )

    refresh_token = login_response.json()["refresh_token"]

    response = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


def test_refresh_rotates_refresh_token(client):
    register_data = {
        "email": "rotation@example.com",
        "password": "password123",
    }

    client.post("/auth/register", json=register_data)

    login_response = client.post(
        "/auth/login",
        json=register_data,
    )

    original_refresh_token = login_response.json()["refresh_token"]

    refresh_response = client.post(
        "/auth/refresh",
        json={"refresh_token": original_refresh_token},
    )

    assert refresh_response.status_code == 200

    rotated_refresh_token = refresh_response.json()["refresh_token"]

    assert rotated_refresh_token != original_refresh_token

    reuse_response = client.post(
        "/auth/refresh",
        json={"refresh_token": original_refresh_token},
    )

    assert reuse_response.status_code == 401

    rotated_response = client.post(
        "/auth/refresh",
        json={"refresh_token": rotated_refresh_token},
    )

    assert rotated_response.status_code == 200


def test_logout_revokes_refresh_token(client):
    register_data = {
        "email": "logout@example.com",
        "password": "password123",
    }

    client.post("/auth/register", json=register_data)

    login_response = client.post(
        "/auth/login",
        json=register_data,
    )

    refresh_token = login_response.json()["refresh_token"]

    logout_response = client.post(
        "/auth/logout",
        json={"refresh_token": refresh_token},
    )

    assert logout_response.status_code == 204

    refresh_response = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert refresh_response.status_code == 401


def test_inactive_user_cannot_login(db, client):
    register_data = {
        "email": "inactive-login@example.com",
        "password": "password123",
    }

    client.post("/auth/register", json=register_data)
    deactivate_user_by_email(db, register_data["email"])

    response = client.post(
        "/auth/login",
        json=register_data,
    )

    assert response.status_code == 401


def test_inactive_user_cannot_use_access_token(db, client):
    register_data = {
        "email": "inactive-access@example.com",
        "password": "password123",
    }

    client.post("/auth/register", json=register_data)

    login_response = client.post(
        "/auth/login",
        json=register_data,
    )

    access_token = login_response.json()["access_token"]
    deactivate_user_by_email(db, register_data["email"])

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 401


def test_inactive_user_cannot_refresh_token(db, client):
    register_data = {
        "email": "inactive-refresh@example.com",
        "password": "password123",
    }

    client.post("/auth/register", json=register_data)

    login_response = client.post(
        "/auth/login",
        json=register_data,
    )

    refresh_token = login_response.json()["refresh_token"]
    deactivate_user_by_email(db, register_data["email"])

    response = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 401


def test_refresh_with_access_token(client):
    register_data = {
        "email": "test2@example.com",
        "password": "password123",
    }

    client.post("/auth/register", json=register_data)

    login_response = client.post(
        "/auth/login",
        json=register_data,
    )

    access_token = login_response.json()["access_token"]

    response = client.post(
        "/auth/refresh",
        json={"refresh_token": access_token},
    )

    assert response.status_code == 401


def test_refresh_with_invalid_token(client):
    response = client.post(
        "/auth/refresh",
        json={"refresh_token": "invalid-token"},
    )

    assert response.status_code == 401
