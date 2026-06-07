import pytest

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


@pytest.fixture
def regular_user(db, client):
    token, user_id = create_user_and_login(
        db,
        client,
        "regular-user@example.com",
    )

    return {
        "token": token,
        "id": user_id,
        "headers": auth_headers(token),
    }


@pytest.fixture
def admin_user(db, client):
    email = "admin-user@example.com"

    token, user_id = create_user_and_login(
        db,
        client,
        email,
    )

    make_admin(db, email)

    return {
        "token": token,
        "id": user_id,
        "headers": auth_headers(token),
    }


def make_admin(db, email: str) -> None:
    user = db.query(User).filter(User.email == email).first()
    user.role = "admin"
    db.commit()


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_list_users_requires_auth(client):
    response = client.get("/users/")

    assert response.status_code == 401


def test_list_users_forbidden_for_regular_user(client, regular_user):
    response = client.get(
        "/users/",
        headers=regular_user["headers"],
    )

    assert response.status_code == 403


def test_admin_can_list_users(client, admin_user):
    response = client.get(
        "/users/",
        headers=admin_user["headers"],
    )

    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_user_can_get_himself(client, regular_user):
    response = client.get(
        f"/users/{regular_user['id']}",
        headers=regular_user["headers"],
    )

    assert response.status_code == 200


def test_user_cannot_get_other_user(db, client, regular_user):
    _, other_user_id = create_user_and_login(
        db,
        client,
        "other@example.com",
    )

    response = client.get(
        f"/users/{other_user_id}",
        headers=regular_user["headers"],
    )

    assert response.status_code == 403


def test_admin_can_get_any_user(db, client, admin_user):
    _, normal_user_id = create_user_and_login(
        db,
        client,
        "normal@example.com",
    )

    response = client.get(
        f"/users/{normal_user_id}",
        headers=admin_user["headers"],
    )

    assert response.status_code == 200


def test_user_can_update_himself(client, regular_user):
    response = client.patch(
        f"/users/{regular_user['id']}",
        json={"email": "updated@example.com"},
        headers=regular_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["email"] == "updated@example.com"


def test_user_cannot_update_other_user(db, client, regular_user):
    _, other_user_id = create_user_and_login(
        db,
        client,
        "userb@example.com",
    )

    response = client.patch(
        f"/users/{other_user_id}",
        json={"email": "hacked@example.com"},
        headers=regular_user["headers"],
    )

    assert response.status_code == 403


def test_admin_can_update_any_user(db, client, admin_user):
    _, user_id = create_user_and_login(
        db,
        client,
        "victim@example.com",
    )

    response = client.patch(
        f"/users/{user_id}",
        json={"email": "updated-admin@example.com"},
        headers=admin_user["headers"],
    )

    assert response.status_code == 200
    assert response.json()["email"] == "updated-admin@example.com"


def test_admin_can_delete_user(db, client, admin_user):
    _, user_id = create_user_and_login(
        db,
        client,
        "victim-delete@example.com",
    )

    response = client.delete(
        f"/users/{user_id}",
        headers=admin_user["headers"],
    )

    assert response.status_code == 204


def test_user_cannot_delete_other_user(db, client, regular_user):
    _, other_user_id = create_user_and_login(
        db,
        client,
        "victim-delete-user@example.com",
    )

    response = client.delete(
        f"/users/{other_user_id}",
        headers=regular_user["headers"],
    )

    assert response.status_code == 403


def test_admin_can_list_users_with_pagination(db, client, admin_user):
    for i in range(15):
        create_user_and_login(
            db,
            client,
            f"pagination-user-{i}@example.com",
        )

    response = client.get(
        "/users/?page=1&size=5",
        headers=admin_user["headers"],
    )

    assert response.status_code == 200
    assert len(response.json()) == 5


def test_admin_can_list_second_page(db, client, admin_user):
    for i in range(15):
        create_user_and_login(
            db,
            client,
            f"pagination-page2-user-{i}@example.com",
        )

    response = client.get(
        "/users/?page=2&size=5",
        headers=admin_user["headers"],
    )

    assert response.status_code == 200
    assert len(response.json()) == 5


def test_pagination_page_must_be_positive(client, admin_user):
    response = client.get(
        "/users/?page=0&size=10",
        headers=admin_user["headers"],
    )

    assert response.status_code == 422


def test_pagination_size_must_be_positive(client, admin_user):
    response = client.get(
        "/users/?page=1&size=0",
        headers=admin_user["headers"],
    )

    assert response.status_code == 422


def test_pagination_size_must_not_exceed_limit(client, admin_user):
    response = client.get(
        "/users/?page=1&size=101",
        headers=admin_user["headers"],
    )

    assert response.status_code == 422