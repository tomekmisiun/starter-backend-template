from app.models.user import User


def create_user_and_login(db, client, email: str) -> tuple[str, int]:
    payload = {
        "email": email,
        "password": "password123",
    }

    client.post("/auth/register", json=payload)

    user = db.query(User).filter(User.email == email).first()

    response = client.post("/auth/login", json=payload)
    token = response.json()["access_token"]

    return token, user.id


def make_admin(db, email: str) -> None:
    user = db.query(User).filter(User.email == email).first()
    user.role = "admin"
    db.commit()


def test_list_users_requires_auth(client):
    response = client.get("/users/")

    assert response.status_code == 401


def test_list_users_forbidden_for_regular_user(db, client):
    token, _ = create_user_and_login(db, client, "user@example.com")

    response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_admin_can_list_users(db, client):
    token, _ = create_user_and_login(db, client, "admin@example.com")
    make_admin(db, "admin@example.com")

    response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_user_can_get_himself(db, client):
    token, user_id = create_user_and_login(db, client, "user1@example.com")

    response = client.get(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200


def test_user_cannot_get_other_user(db, client):
    token, _ = create_user_and_login(db, client, "user2@example.com")
    _, other_user_id = create_user_and_login(db, client, "other@example.com")

    response = client.get(
        f"/users/{other_user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_admin_can_get_any_user(db, client):
    token, _ = create_user_and_login(db, client, "admin2@example.com")
    make_admin(db, "admin2@example.com")

    _, normal_user_id = create_user_and_login(db, client, "normal@example.com")

    response = client.get(
        f"/users/{normal_user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200


def test_user_can_update_himself(db, client):
    token, user_id = create_user_and_login(db, client, "patch@example.com")

    response = client.patch(
        f"/users/{user_id}",
        json={"email": "updated@example.com"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "updated@example.com"


def test_user_cannot_update_other_user(db, client):
    token, _ = create_user_and_login(db, client, "usera@example.com")

    _, other_user_id = create_user_and_login(
        db,
        client,
        "userb@example.com",
    )

    response = client.patch(
        f"/users/{other_user_id}",
        json={"email": "hacked@example.com"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_admin_can_update_any_user(db, client):
    token, _ = create_user_and_login(
        db,
        client,
        "admin3@example.com",
    )

    make_admin(db, "admin3@example.com")

    _, user_id = create_user_and_login(
        db,
        client,
        "victim@example.com",
    )

    response = client.patch(
        f"/users/{user_id}",
        json={"email": "updated-admin@example.com"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "updated-admin@example.com"


def test_admin_can_delete_user(db, client):
    token, _ = create_user_and_login(
        db,
        client,
        "admin-delete@example.com",
    )

    make_admin(db, "admin-delete@example.com")

    _, user_id = create_user_and_login(
        db,
        client,
        "victim-delete@example.com",
    )

    response = client.delete(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204


def test_user_cannot_delete_other_user(db, client):
    token, _ = create_user_and_login(
        db,
        client,
        "user-delete@example.com",
    )

    _, other_user_id = create_user_and_login(
        db,
        client,
        "victim-delete@example.com",
    )

    response = client.delete(
        f"/users/{other_user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403