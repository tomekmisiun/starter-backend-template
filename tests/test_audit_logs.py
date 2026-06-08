import pytest

from app.models.audit_log import AuditLog
from app.models.user import User


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


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


def make_admin(db, user_id: int) -> None:
    user = db.query(User).filter(User.id == user_id).first()
    user.role = "admin"
    db.commit()


@pytest.fixture
def admin_user(db, client):
    token, user_id = create_user_and_login(
        db,
        client,
        "audit-admin@example.com",
    )

    make_admin(db, user_id)

    return {
        "id": user_id,
        "headers": auth_headers(token),
    }


@pytest.fixture
def regular_user(db, client):
    token, user_id = create_user_and_login(
        db,
        client,
        "audit-user@example.com",
    )

    return {
        "id": user_id,
        "headers": auth_headers(token),
    }


def get_latest_audit_log(db) -> AuditLog:
    return db.query(AuditLog).order_by(AuditLog.id.desc()).first()


def test_admin_update_user_creates_audit_log(
    db,
    client,
    admin_user,
    regular_user,
):
    response = client.patch(
        f"/users/{regular_user['id']}",
        json={"email": "audit-updated@example.com"},
        headers=admin_user["headers"],
    )

    assert response.status_code == 200

    audit_log = get_latest_audit_log(db)

    assert audit_log.admin_id == admin_user["id"]
    assert audit_log.action == "user.updated"
    assert audit_log.target_user_id == regular_user["id"]


def test_self_update_does_not_create_audit_log(db, client, regular_user):
    audit_log_count = db.query(AuditLog).count()

    response = client.patch(
        f"/users/{regular_user['id']}",
        json={"email": "audit-self-updated@example.com"},
        headers=regular_user["headers"],
    )

    assert response.status_code == 200
    assert db.query(AuditLog).count() == audit_log_count


def test_admin_deactivate_user_creates_audit_log(
    db,
    client,
    admin_user,
    regular_user,
):
    response = client.patch(
        f"/users/{regular_user['id']}/deactivate",
        headers=admin_user["headers"],
    )

    assert response.status_code == 200

    audit_log = get_latest_audit_log(db)

    assert audit_log.admin_id == admin_user["id"]
    assert audit_log.action == "user.deactivated"
    assert audit_log.target_user_id == regular_user["id"]


def test_admin_activate_user_creates_audit_log(
    db,
    client,
    admin_user,
    regular_user,
):
    client.patch(
        f"/users/{regular_user['id']}/deactivate",
        headers=admin_user["headers"],
    )

    response = client.patch(
        f"/users/{regular_user['id']}/activate",
        headers=admin_user["headers"],
    )

    assert response.status_code == 200

    audit_log = get_latest_audit_log(db)

    assert audit_log.admin_id == admin_user["id"]
    assert audit_log.action == "user.activated"
    assert audit_log.target_user_id == regular_user["id"]


def test_admin_delete_user_creates_audit_log(
    db,
    client,
    admin_user,
):
    _, target_user_id = create_user_and_login(
        db,
        client,
        "audit-delete@example.com",
    )

    response = client.delete(
        f"/users/{target_user_id}",
        headers=admin_user["headers"],
    )

    assert response.status_code == 204

    audit_log = get_latest_audit_log(db)

    assert audit_log.admin_id == admin_user["id"]
    assert audit_log.action == "user.deleted"
    assert audit_log.target_user_id == target_user_id


def test_list_audit_logs_requires_auth(client):
    response = client.get("/admin/audit-logs")

    assert response.status_code == 401


def test_list_audit_logs_forbidden_for_regular_user(client, regular_user):
    response = client.get(
        "/admin/audit-logs",
        headers=regular_user["headers"],
    )

    assert response.status_code == 403


def test_admin_can_list_audit_logs(db, client, admin_user, regular_user):
    client.patch(
        f"/users/{regular_user['id']}/deactivate",
        headers=admin_user["headers"],
    )

    response = client.get(
        "/admin/audit-logs",
        headers=admin_user["headers"],
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) >= 1
    assert data[0]["admin_id"] == admin_user["id"]
    assert data[0]["action"] == "user.deactivated"
    assert data[0]["target_user_id"] == regular_user["id"]
    assert "created_at" in data[0]
