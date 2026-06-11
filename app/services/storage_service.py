from dataclasses import dataclass
from uuid import uuid4

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.file_validation import (
    ensure_malware_scan_is_clean,
    run_malware_scan,
    validate_content_sniff,
    validate_declared_content_type,
)
from app.core.permissions import Permission
from app.models.uploaded_file import UploadedFile
from app.models.user import User
from app.services.permission_service import user_has_permission
from app.services.tenant_service import build_tenant_object_key_prefix


@dataclass(frozen=True)
class StoredObject:
    object_key: str
    size_bytes: int


@dataclass(frozen=True)
class PresignedUrl:
    url: str
    expires_in_seconds: int


class S3StorageProvider:
    def __init__(self):
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key_id,
            aws_secret_access_key=settings.s3_secret_access_key,
            region_name=settings.s3_region_name,
        )

    def upload_file(
        self,
        *,
        object_key: str,
        body: bytes,
        content_type: str,
    ) -> None:
        self.client.put_object(
            Bucket=settings.s3_bucket_name,
            Key=object_key,
            Body=body,
            ContentType=content_type,
        )

    def delete_object(self, *, object_key: str) -> None:
        self.client.delete_object(
            Bucket=settings.s3_bucket_name,
            Key=object_key,
        )

    def object_exists(self, *, object_key: str) -> bool:
        try:
            self.client.head_object(
                Bucket=settings.s3_bucket_name,
                Key=object_key,
            )
        except ClientError:
            return False

        return True

    def generate_presigned_download_url(self, *, object_key: str) -> PresignedUrl:
        url = self.client.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": settings.s3_bucket_name,
                "Key": object_key,
            },
            ExpiresIn=settings.upload_presigned_url_expire_seconds,
        )

        return PresignedUrl(
            url=url,
            expires_in_seconds=settings.upload_presigned_url_expire_seconds,
        )

    def generate_presigned_upload_url(
        self,
        *,
        object_key: str,
        content_type: str,
    ) -> PresignedUrl:
        url = self.client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": settings.s3_bucket_name,
                "Key": object_key,
                "ContentType": content_type,
            },
            ExpiresIn=settings.upload_presigned_url_expire_seconds,
        )

        return PresignedUrl(
            url=url,
            expires_in_seconds=settings.upload_presigned_url_expire_seconds,
        )

    def verify_bucket_access(self) -> None:
        try:
            self.client.head_bucket(Bucket=settings.s3_bucket_name)
        except (BotoCoreError, ClientError) as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Object storage bucket is not reachable",
            ) from exc


class StorageService:
    def __init__(self, provider: S3StorageProvider | None = None):
        self.provider = provider or S3StorageProvider()

    def upload(
        self,
        *,
        owner: User,
        file: UploadFile,
        db: Session,
    ) -> UploadedFile:
        content_type = file.content_type or "application/octet-stream"
        validate_declared_content_type(content_type)
        body = read_upload_body(file)
        validate_file_size(len(body))
        validate_content_sniff(content_type, body)
        ensure_malware_scan_is_clean(run_malware_scan(body, file.filename or "upload"))

        object_key = build_object_key(
            owner.tenant_id,
            owner.id,
            file.filename or "upload",
        )

        try:
            self.provider.upload_file(
                object_key=object_key,
                body=body,
                content_type=content_type,
            )
        except (BotoCoreError, ClientError) as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Object storage upload failed",
            ) from exc

        uploaded_file = UploadedFile(
            tenant_id=owner.tenant_id,
            owner_id=owner.id,
            object_key=object_key,
            filename=file.filename or "upload",
            content_type=content_type,
            size_bytes=len(body),
        )

        db.add(uploaded_file)
        db.commit()
        db.refresh(uploaded_file)

        return uploaded_file

    def create_presigned_upload(
        self,
        *,
        owner: User,
        filename: str,
        content_type: str,
    ) -> tuple[str, PresignedUrl]:
        validate_declared_content_type(content_type)
        self.provider.verify_bucket_access()
        object_key = build_object_key(owner.tenant_id, owner.id, filename)
        presigned_url = self.provider.generate_presigned_upload_url(
            object_key=object_key,
            content_type=content_type,
        )

        return object_key, presigned_url

    def complete_presigned_upload(
        self,
        *,
        owner: User,
        object_key: str,
        filename: str,
        content_type: str,
        size_bytes: int,
        db: Session,
    ) -> UploadedFile:
        validate_declared_content_type(content_type)
        validate_file_size(size_bytes)
        ensure_object_key_belongs_to_owner(
            object_key=object_key,
            owner=owner,
        )

        if not self.provider.object_exists(object_key=object_key):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded object was not found in storage",
            )

        uploaded_file = UploadedFile(
            tenant_id=owner.tenant_id,
            owner_id=owner.id,
            object_key=object_key,
            filename=filename,
            content_type=content_type,
            size_bytes=size_bytes,
        )

        db.add(uploaded_file)
        db.commit()
        db.refresh(uploaded_file)

        return uploaded_file

    def get_presigned_download_url(
        self,
        *,
        uploaded_file: UploadedFile,
        current_user: User,
    ) -> PresignedUrl:
        if not can_access_uploaded_file(current_user, uploaded_file):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        try:
            return self.provider.generate_presigned_download_url(
                object_key=uploaded_file.object_key,
            )
        except (BotoCoreError, ClientError) as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Object storage download URL generation failed",
            ) from exc

    def delete_uploaded_file(
        self,
        *,
        uploaded_file: UploadedFile,
        current_user: User,
        db: Session,
    ) -> None:
        if not can_delete_uploaded_file(current_user, uploaded_file):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        try:
            self.provider.delete_object(object_key=uploaded_file.object_key)
        except (BotoCoreError, ClientError) as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Object storage delete failed",
            ) from exc

        db.delete(uploaded_file)
        db.commit()

    def verify_bucket_access(self) -> None:
        self.provider.verify_bucket_access()


def get_storage_service() -> StorageService:
    return StorageService()


def get_uploaded_file(
    db: Session,
    *,
    file_id: int,
    tenant_id: int,
) -> UploadedFile | None:
    return (
        db.query(UploadedFile)
        .filter(
            UploadedFile.id == file_id,
            UploadedFile.tenant_id == tenant_id,
        )
        .first()
    )


def can_access_uploaded_file(current_user: User, uploaded_file: UploadedFile) -> bool:
    if current_user.tenant_id != uploaded_file.tenant_id:
        return False

    if user_has_permission(current_user, Permission.FILES_DOWNLOAD):
        return True

    return (
        uploaded_file.owner_id == current_user.id
        and user_has_permission(current_user, Permission.FILES_DOWNLOAD_SELF)
    )


def can_delete_uploaded_file(current_user: User, uploaded_file: UploadedFile) -> bool:
    if current_user.tenant_id != uploaded_file.tenant_id:
        return False

    if user_has_permission(current_user, Permission.FILES_DELETE):
        return True

    return (
        uploaded_file.owner_id == current_user.id
        and user_has_permission(current_user, Permission.FILES_DELETE_SELF)
    )


def validate_file_size(size_bytes: int) -> None:
    if size_bytes > settings.upload_max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="File too large",
        )


def read_upload_body(file: UploadFile) -> bytes:
    return file.file.read()


def build_object_key(tenant_id: int, owner_id: int, filename: str) -> str:
    safe_filename = filename.replace("/", "_").replace("\\", "_")
    tenant_prefix = build_tenant_object_key_prefix(tenant_id)
    return f"{tenant_prefix}/uploads/{owner_id}/{uuid4().hex}-{safe_filename}"


def ensure_object_key_belongs_to_owner(*, object_key: str, owner: User) -> None:
    expected_prefix = (
        f"{build_tenant_object_key_prefix(owner.tenant_id)}/uploads/{owner.id}/"
    )

    if not object_key.startswith(expected_prefix):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid object key for current user",
        )
