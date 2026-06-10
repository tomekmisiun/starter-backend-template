from app.models.uploaded_file import UploadedFile


class FakeStorageService:
    def __init__(self):
        self.uploads = []

    def upload(self, *, owner, file, db):
        body = file.file.read()
        self.uploads.append(
            {
                "owner_id": owner.id,
                "filename": file.filename,
                "content_type": file.content_type,
                "body": body,
            }
        )

        uploaded_file = UploadedFile(
            owner_id=owner.id,
            object_key=f"uploads/{owner.id}/{file.filename}",
            filename=file.filename,
            content_type=file.content_type,
            size_bytes=len(body),
        )

        db.add(uploaded_file)
        db.commit()
        db.refresh(uploaded_file)

        return uploaded_file


def create_user_and_login(client):
    payload = {
        "email": "file-user@example.com",
        "password": "password123",
    }
    client.post("/auth/register", json=payload)
    response = client.post("/auth/login", json=payload)

    return response.json()["access_token"]


def test_upload_requires_auth(client):
    response = client.post(
        "/files/upload",
        files={"file": ("example.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 401


def test_authenticated_user_can_upload_file(client, monkeypatch):
    storage_service = FakeStorageService()
    monkeypatch.setattr(
        "app.api.routes.files.get_storage_service",
        lambda: storage_service,
    )
    token = create_user_and_login(client)

    response = client.post(
        "/files/upload",
        files={"file": ("example.pdf", b"file-content", "application/pdf")},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201

    data = response.json()
    upload = storage_service.uploads[0]

    assert data["filename"] == "example.pdf"
    assert data["content_type"] == "application/pdf"
    assert data["size_bytes"] == len(b"file-content")
    assert upload["filename"] == "example.pdf"
    assert upload["body"] == b"file-content"


def test_upload_rejects_unsupported_content_type(client):
    token = create_user_and_login(client)

    response = client.post(
        "/files/upload",
        files={"file": ("example.txt", b"hello", "text/plain")},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400


def test_upload_rejects_files_above_size_limit(client, monkeypatch):
    monkeypatch.setattr("app.services.storage_service.settings.upload_max_size_bytes", 4)
    token = create_user_and_login(client)

    response = client.post(
        "/files/upload",
        files={"file": ("example.pdf", b"too-large", "application/pdf")},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 413
