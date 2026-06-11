from botocore.exceptions import ClientError

from app.models.uploaded_file import UploadedFile
from app.services.storage_service import PresignedUrl, StorageService


PDF_BYTES = b"%PDF-1.4 test-content"
PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"png-content"


class FakeStorageProvider:
    def __init__(self):
        self.objects: dict[str, bytes] = {}
        self.deleted_keys: list[str] = []
        self.bucket_ready = True

    def upload_file(self, *, object_key: str, body: bytes, content_type: str) -> None:
        if not self.bucket_ready:
            raise ClientError(
                {"Error": {"Code": "500", "Message": "bucket unavailable"}},
                "PutObject",
            )
        self.objects[object_key] = body

    def delete_object(self, *, object_key: str) -> None:
        self.deleted_keys.append(object_key)
        self.objects.pop(object_key, None)

    def object_exists(self, *, object_key: str) -> bool:
        return object_key in self.objects

    def generate_presigned_download_url(self, *, object_key: str) -> PresignedUrl:
        return PresignedUrl(
            url=f"https://storage.example/{object_key}",
            expires_in_seconds=300,
        )

    def generate_presigned_upload_url(
        self,
        *,
        object_key: str,
        content_type: str,
    ) -> PresignedUrl:
        return PresignedUrl(
            url=f"https://storage.example/upload/{object_key}",
            expires_in_seconds=300,
        )

    def verify_bucket_access(self) -> None:
        if not self.bucket_ready:
            raise ClientError(
                {"Error": {"Code": "404", "Message": "bucket unavailable"}},
                "HeadBucket",
            )


class FakeStorageService(StorageService):
    def __init__(self):
        self.provider = FakeStorageProvider()
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
            tenant_id=owner.tenant_id,
            owner_id=owner.id,
            object_key=f"tenants/{owner.tenant_id}/uploads/{owner.id}/{file.filename}",
            filename=file.filename,
            content_type=file.content_type,
            size_bytes=len(body),
        )

        db.add(uploaded_file)
        db.commit()
        db.refresh(uploaded_file)

        return uploaded_file


def create_user_and_login(client, email="file-user@example.com"):
    payload = {
        "email": email,
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
        files={"file": ("example.pdf", PDF_BYTES, "application/pdf")},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201

    data = response.json()
    upload = storage_service.uploads[0]

    assert data["filename"] == "example.pdf"
    assert data["content_type"] == "application/pdf"
    assert data["size_bytes"] == len(PDF_BYTES)
    assert upload["filename"] == "example.pdf"
    assert upload["body"] == PDF_BYTES


def test_upload_rejects_unsupported_content_type(client):
    token = create_user_and_login(client)

    response = client.post(
        "/files/upload",
        files={"file": ("example.txt", b"hello", "text/plain")},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400


def test_upload_rejects_content_type_and_sniff_mismatch(client, monkeypatch):
    monkeypatch.setattr(
        "app.api.routes.files.get_storage_service",
        lambda: StorageService(provider=FakeStorageProvider()),
    )
    token = create_user_and_login(client, email="sniff-user@example.com")

    response = client.post(
        "/files/upload",
        files={"file": ("example.pdf", PNG_BYTES, "application/pdf")},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400


def test_upload_rejects_files_above_size_limit(client, monkeypatch):
    monkeypatch.setattr("app.services.storage_service.settings.upload_max_size_bytes", 4)
    token = create_user_and_login(client, email="size-user@example.com")

    response = client.post(
        "/files/upload",
        files={"file": ("example.pdf", PDF_BYTES, "application/pdf")},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 413


def test_user_can_get_presigned_download_url_for_own_file(client, monkeypatch):
    provider = FakeStorageProvider()
    monkeypatch.setattr(
        "app.api.routes.files.get_storage_service",
        lambda: StorageService(provider=provider),
    )
    token = create_user_and_login(client, email="download-user@example.com")

    upload_response = client.post(
        "/files/upload",
        files={"file": ("example.pdf", PDF_BYTES, "application/pdf")},
        headers={"Authorization": f"Bearer {token}"},
    )
    file_id = upload_response.json()["id"]

    response = client.get(
        f"/files/{file_id}/download-url",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["download_url"].endswith(upload_response.json()["object_key"])
    assert response.json()["expires_in_seconds"] == 300


def test_user_cannot_download_other_users_file(client, monkeypatch):
    provider = FakeStorageProvider()
    monkeypatch.setattr(
        "app.api.routes.files.get_storage_service",
        lambda: StorageService(provider=provider),
    )
    owner_token = create_user_and_login(client, email="owner-user@example.com")
    other_token = create_user_and_login(client, email="other-user@example.com")

    upload_response = client.post(
        "/files/upload",
        files={"file": ("example.pdf", PDF_BYTES, "application/pdf")},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    file_id = upload_response.json()["id"]

    response = client.get(
        f"/files/{file_id}/download-url",
        headers={"Authorization": f"Bearer {other_token}"},
    )

    assert response.status_code == 403


def test_user_can_delete_own_file(client, monkeypatch):
    provider = FakeStorageProvider()
    monkeypatch.setattr(
        "app.api.routes.files.get_storage_service",
        lambda: StorageService(provider=provider),
    )
    token = create_user_and_login(client, email="delete-user@example.com")

    upload_response = client.post(
        "/files/upload",
        files={"file": ("example.pdf", PDF_BYTES, "application/pdf")},
        headers={"Authorization": f"Bearer {token}"},
    )
    object_key = upload_response.json()["object_key"]
    file_id = upload_response.json()["id"]

    response = client.delete(
        f"/files/{file_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204
    assert provider.deleted_keys == [object_key]


def test_upload_returns_503_when_storage_is_unavailable(client, monkeypatch):
    provider = FakeStorageProvider()
    provider.bucket_ready = False
    monkeypatch.setattr(
        "app.api.routes.files.get_storage_service",
        lambda: StorageService(provider=provider),
    )
    token = create_user_and_login(client, email="storage-fail@example.com")

    response = client.post(
        "/files/upload",
        files={"file": ("example.pdf", PDF_BYTES, "application/pdf")},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 503
